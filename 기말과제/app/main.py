# ───────────────────────── Path Fix (맨 위 고정) ─────────────────────────
import os, sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]   # pjh 루트
os.environ["PYTHONPATH"] = str(BASE_DIR)         # ✅ 리로더에게도 PYTHONPATH 전달
os.chdir(BASE_DIR)                               # ✅ 작업 디렉토리 고정
sys.path.insert(0, str(BASE_DIR))                # ✅ backend import 가능
print(">>> WORKDIR:", os.getcwd())
print(">>> PYTHONPATH:", sys.path[0])

# ───────────────────────── 표준/외부 모듈 ─────────────────────────
import re
import random
from typing import Optional, List, Dict, Any

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from pydantic import BaseModel

# ───────────────────────── 내부 모듈 (backend.core.*) ─────────────────────────
try:
    from backend.core.gemini_client import summarize_text_ko, rank_courses_ko
except Exception:
    def summarize_text_ko(text: str) -> str:
        return text[:200] + ("..." if len(text) > 200 else "")
    def rank_courses_ko(prefs: str, courses: list, topk: int = 5):
        return courses[:topk]

from backend.core.scheduler import (
    solve, Course, Room, Instructor, Grid, Hard, Soft, Request
)
from backend.core.room_monitor import load_usage_data, get_current_empty_rooms

# ───────────────────────── Env & DB ─────────────────────────
# 루트(pjh/.env) 로드
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)

DEFAULT_SQLITE = "sqlite:///./courses.db"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_SQLITE)

if DATABASE_URL.startswith("sqlite:///./"):
    db_file = Path(__file__).resolve().parents[2] / DATABASE_URL.replace("sqlite:///./", "")
    DATABASE_URL = f"sqlite:///{db_file.as_posix()}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
DB_DIALECT = engine.dialect.name

# ───────────────────────── FastAPI ─────────────────────────
app = FastAPI(title="Courses API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONT_DIR = Path(__file__).resolve().parents[2] / "frontend"
if FRONT_DIR.exists():
    app.mount("/app", StaticFiles(directory=str(FRONT_DIR), html=True), name="static")

# ───────────────────────── Schemas ─────────────────────────
class SummaryIn(BaseModel):
    text: str

class RecommendIn(BaseModel):
    preferences: str
    limit: int = 5

class ScheduleIn(BaseModel):
    days: List[str] = ["MON", "TUE", "WED", "THU", "FRI"]
    periodsPerDay: int = 9
    blockMinutes: int = 50
    preferMorning: bool = True
    priorityWeight: int = 1
    natural: str = ""
    noFridayEvening: bool = False

# ───────────────────────── 공통 유틸 ─────────────────────────
def _to_int(x, default=0):
    if x is None:
        return default
    if isinstance(x, int):
        return x
    s = str(x).strip()
    if s == "" or s.lower() == "nan":
        return default
    s = re.sub(r"[^0-9\-]", "", s)
    try:
        return int(s) if s not in ("", "-") else default
    except Exception:
        return default

def _pick_name_col(cols):
    for k in ["교과목명", "과목명", "name", "NAME"]:
        if k in cols:
            return k
    return cols[0] if cols else "교과목명"

# ───────────────────────── Endpoints ─────────────────────────
@app.get("/health")
def health():
    return {"ok": True, "db": DATABASE_URL, "dialect": DB_DIALECT}

@app.get("/courses")
def courses(limit: int = 20, offset: int = 0):
    with engine.connect() as c:
        df = pd.read_sql(text(f"SELECT * FROM courses LIMIT {int(limit)} OFFSET {int(offset)}"), c)
    return df.to_dict(orient="records")

@app.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = 100, offset: int = 0):
    try:
        q = (q or "").strip()
        if not q:
            return {"total": 0, "results": []}

        with engine.connect() as c:
            cols = pd.read_sql(text("SELECT * FROM courses LIMIT 1"), c).columns.tolist()
            name_col = _pick_name_col(cols)

            if DB_DIALECT == "postgresql":
                sql = text(f'''
                    SELECT * FROM courses
                    WHERE CAST("{name_col}" AS TEXT) ILIKE :kw
                    ORDER BY 1
                    LIMIT {int(limit)} OFFSET {int(offset)}
                ''')
                cnt_sql = text(f'''
                    SELECT COUNT(*) FROM courses
                    WHERE CAST("{name_col}" AS TEXT) ILIKE :kw
                ''')
                params = {"kw": f"%{q}%"}

            else:
                sql = text(f'''
                    SELECT * FROM courses
                    WHERE LOWER(CAST("{name_col}" AS TEXT)) LIKE :kw
                    ORDER BY 1
                    LIMIT {int(limit)} OFFSET {int(offset)}
                ''')
                cnt_sql = text(f'''
                    SELECT COUNT(*) FROM courses
                    WHERE LOWER(CAST("{name_col}" AS TEXT)) LIKE :kw
                ''')
                params = {"kw": f"%{q.lower()}%"}

            df = pd.read_sql(sql, c, params=params)
            total = c.execute(cnt_sql, params).scalar() or 0

        return {"total": int(total), "results": df.to_dict(orient="records")}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"/search 실패: {e}"})

@app.post("/gemini/summary")
def gemini_summary(body: SummaryIn):
    return {"summary": summarize_text_ko(body.text)}

@app.post("/gemini/recommend")
def gemini_recommend(body: RecommendIn):
    topk = max(1, min(body.limit, 10))
    with engine.connect() as c:
        df = pd.read_sql(text("SELECT * FROM courses"), c)
    courses = df.to_dict(orient="records")
    res = rank_courses_ko(body.preferences, courses, topk=topk)
    return {"result": res}

# ───────────────────────── 실시간 공실 API ─────────────────────────
@app.get("/v1/rooms/empty")
def api_empty_rooms():
    df = load_usage_data()
    empty_rooms = get_current_empty_rooms(df)
    return {"timestamp": pd.Timestamp.now().isoformat(), "empty_rooms": empty_rooms}

# ───────────────────────── Entry ─────────────────────────
if __name__ == "__main__":
    import uvicorn
    # ✅ 루트(pjh)에서 실행해야 함
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
