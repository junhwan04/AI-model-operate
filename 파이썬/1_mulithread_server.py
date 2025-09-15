'''
동작 방식

서버 실행 → 127.0.0.1:9999에서 접속 대기

클라이언트 실행 → 서버에 연결 요청

서버는 accept() 후 새로운 쓰레드 생성하여 클라이언트 처리

클라이언트는 메시지를 보내고, 서버는 받은 메시지를 다시 돌려줌 (Echo)

여러 클라이언트를 실행하면 서버는 각 클라이언트를 쓰레드로 병렬 처리

'''


import socket
import threading

# 클라이언트와 통신하는 함수
def handle_client(client_socket, addr):
    print(f"[연결됨] 클라이언트 {addr} 접속")

    while True:
        try:
            # 클라이언트로부터 데이터 수신
            data = client_socket.recv(1024)
            if not data:
                print(f"[종료] 클라이언트 {addr} 연결 종료")
                break
            print(f"[메시지 수신] {addr}: {data.decode()}")
            
            # 받은 데이터를 클라이언트에게 다시 전송 (에코 서버)
            client_socket.sendall(data)
        except:
            break
    
    client_socket.close()

def start_server():
    # 서버 소켓 생성 (IPv4, TCP)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 9999))  # localhost, 포트 9999
    server.listen(5)  # 최대 5명까지 대기
    print("[서버 시작] 127.0.0.1:9999 에서 대기중...")

    while True:
        client_socket, addr = server.accept()
        # 클라이언트마다 새로운 쓰레드 실행
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()
        print(f"[현재 접속자 수] {threading.active_count() - 1}")  # main thread 제외

if __name__ == "__main__":
    start_server()
