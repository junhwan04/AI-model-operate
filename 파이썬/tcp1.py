import socket

def tcp_server():
    host = "127.0.0.1"   # 로컬호스트
    port = 5000          # 포트 번호
    
    # TCP 소켓 생성
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))   # 바인딩
    server_socket.listen(1)            # 연결 대기
    
    print(f"TCP 서버 실행 중... (포트 {port})")
    conn, addr = server_socket.accept()  # 클라이언트 연결 수락
    print("클라이언트 연결:", addr)
    
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        print("클라이언트 메시지:", data)
        conn.send(f"서버 응답: {data}".encode())
    
    conn.close()

if __name__ == "__main__":
    tcp_server()
