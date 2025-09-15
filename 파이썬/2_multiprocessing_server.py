import socket
import multiprocessing

# 클라이언트와 통신하는 함수
def handle_client(client_socket, address):
    print(f"[연결됨] 클라이언트 {address}")
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:  # 클라이언트가 연결 종료
                print(f"[종료] 클라이언트 {address}")
                break
            print(f"[메시지 수신] {address}: {data.decode()}")
            client_socket.sendall(data)  # 에코 서버: 받은 데이터를 그대로 돌려줌
        except ConnectionResetError:
            print(f"[비정상 종료] 클라이언트 {address}")
            break
    client_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 5000))  # 모든 네트워크 인터페이스에서 5000번 포트 리스닝
    server_socket.listen()
    print("[서버 실행 중] 포트 5000에서 대기...")

    while True:
        client_socket, addr = server_socket.accept()  # 클라이언트 연결 수락
        print(f"[접속 요청] {addr}")

        # 각 클라이언트별 독립적인 프로세스 생성
        process = multiprocessing.Process(target=handle_client, args=(client_socket, addr))
        process.start()

        # 메인 프로세스는 소켓을 닫아야 자식 프로세스에 소켓 핸들이 안전하게 위임됨
        client_socket.close()

if __name__ == "__main__":
    main()
