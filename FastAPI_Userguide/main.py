from typing import List, Optional
from datetime import datetime, time, timedelta
from uuid import UUID

from fastapi import FastAPI, Query, Path, Body, Depends
from pydantic import BaseModel, Field

app = FastAPI(title="FastAPI Userguide Examples")

# ============================================================
# 1. Tutorial - User Guide / First Steps
#    - 기본 예제
# ============================================================

@app.get("/")
def read_root():
    """첫걸음(First Steps) 예제"""
    return {"message": "Hello FastAPI - First Steps"}


@app.get("/items/{item_id}")
def read_item_first_steps(item_id: int, q: Optional[str] = None):
    """경로 + 선택 쿼리 매개변수 기본 예제"""
    response = {"item_id": item_id}
    if q:
        response["q"] = q
    return response


# ============================================================
# 2. Path Parameters (경로 매개변수)
# ============================================================

@app.get("/users/{user_id}")
def read_user(user_id: str):
    """문자열 타입 경로 매개변수 예제"""
    return {"user_id": user_id}


# ============================================================
# 3. Query Parameters (쿼리 매개변수)
# ============================================================

@app.get("/items/")
def read_items(q: Optional[str] = None, skip: int = 0, limit: int = 10):
    """
    기본 쿼리 매개변수 예제
    - /items/?q=hello&skip=10&limit=5
    """
    fake_items_db = [{"item_id": i} for i in range(100)]
    result = fake_items_db[skip : skip + limit]
    if q:
        return {"q": q, "items": result}
    return {"items": result}


# ============================================================
# 4. Request Body (요청 본문)
# ============================================================

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


@app.post("/items/")
def create_item(item: Item):
    """요청 본문으로 Item 모델 받기"""
    price_with_tax = item.price + (item.tax or 0)
    return {"item": item, "price_with_tax": price_with_tax}


# ============================================================
# 5. Query Parameters and String Validations
#    (쿼리 매개변수와 문자열 검증)
# ============================================================

@app.get("/search/")
def search_items(
    q: Optional[str] = Query(
        default=None,
        min_length=3,
        max_length=50,
        regex="^[a-zA-Z0-9 _-]+$",
        description="검색어 (영문/숫자/공백/_- 만 허용)",
    )
):
    return {"query": q}


# ============================================================
# 6. Path Parameters and Numeric Validations
#    (경로 매개변수와 숫자 검증)
# ============================================================

@app.get("/orders/{order_id}")
def get_order(
    order_id: int = Path(
        ...,
        gt=0,
        le=1000,
        description="1 이상 1000 이하의 주문 ID",
    )
):
    return {"order_id": order_id}


# ============================================================
# 7. Query Parameter Models
#    (쿼리 매개변수 모델)
# ============================================================

class CommonQueryParams(BaseModel):
    q: Optional[str] = None
    skip: int = 0
    limit: int = 10


def common_parameters(
    q: Optional[str] = Query(None, max_length=50),
    skip: int = 0,
    limit: int = 10,
) -> CommonQueryParams:
    """여러 엔드포인트에서 공통으로 쓸 쿼리 파라미터"""
    return CommonQueryParams(q=q, skip=skip, limit=limit)


@app.get("/items-with-common")
def read_items_with_common(common: CommonQueryParams = Depends(common_parameters)):
    """
    쿼리 매개변수 모델을 의존성으로 사용하는 예제
    - /items-with-common?q=hello&skip=5&limit=3
    """
    return {"common_params": common}


# ============================================================
# 8. Body - Multiple Parameters
#    (본문 - 다중 매개변수)
# ============================================================

class User(BaseModel):
    username: str
    full_name: Optional[str] = None


@app.post("/items-with-user")
def create_item_with_user(
    item: Item,
    user: User,
    importance: int = Body(..., description="중요도 점수"),
):
    """
    본문으로 여러 모델 + 추가 값 받기
    - body 안에 item, user, importance 모두 포함
    """
    return {"item": item, "user": user, "importance": importance}


# ============================================================
# 9. Body - Fields
#    (본문 - 필드 / Field 사용)
# ============================================================

class ItemWithField(BaseModel):
    name: str = Field(..., title="상품 이름", max_length=50)
    description: Optional[str] = Field(
        default=None,
        title="설명",
        max_length=300,
        description="상품에 대한 상세 설명",
    )
    price: float = Field(..., gt=0, description="0보다 큰 가격")
    tax: Optional[float] = Field(default=None, ge=0)


@app.post("/items-with-fields")
def create_item_with_field(item: ItemWithField):
    return item


# ============================================================
# 10. Body - Nested Models
#     (본문 - 중첩 모델)
# ============================================================

class Image(BaseModel):
    url: str
    name: str


class ItemNested(BaseModel):
    name: str
    price: float
    tags: List[str] = []
    image: Optional[Image] = None


@app.post("/items-nested")
def create_item_nested(item: ItemNested):
    """중첩 모델(Image)과 리스트(tags)를 포함한 본문 예제"""
    return item


# ============================================================
# 11. Declare Request Example Data
#     (요청 예제 데이터 선언)
# ============================================================

@app.post("/items-with-example")
def create_item_with_example(
    item: ItemWithField = Body(
        ...,
        examples={
            "normal": {
                "summary": "일반 예시",
                "description": "가장 기본적인 요청 예제",
                "value": {
                    "name": "Keyboard",
                    "description": "mechanical keyboard",
                    "price": 99000,
                    "tax": 9000,
                },
            },
            "cheap": {
                "summary": "저렴한 상품",
                "value": {
                    "name": "Mouse",
                    "description": "simple mouse",
                    "price": 10000,
                    "tax": 0,
                },
            },
        },
    ),
):
    """
    스웨거(/docs)에서 예제 데이터가 보이도록 설정
    """
    return item


# ============================================================
# 12. Extra Data Types
#     (추가 데이터 자료형)
# ============================================================

class Schedule(BaseModel):
    start_datetime: datetime
    end_datetime: datetime
    repeat_at: time
    process_after: timedelta


@app.put("/schedules/{task_id}")
def update_schedule(task_id: UUID, schedule: Schedule):
    """
    datetime, time, timedelta, UUID 같은 추가 자료형 예제
    - task_id: UUID 타입 경로 매개변수
    """
    return {
        "task_id": task_id,
        "schedule": schedule,
    }
