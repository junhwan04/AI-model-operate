'''
멀티 클라이언트 테스트
서버 켜둔 상태에서 클라이언트를 두 개 실행해보면, 서버 쪽에 이런 로그가 찍혀야 합니다:

[연결됨] 클라이언트 ('127.0.0.1', 12345) 접속
[현재 접속자 수] 1

'''


import socket

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 9999))  # 서버에 연결
    print("[서버 연결 완료]")

    while True:
        msg = input("메시지 입력 (종료: exit): ")
        if msg.lower() == "exit":
            break
        client.sendall(msg.encode())
        data = client.recv(1024)
        print(f"[서버 응답] {data.decode()}")

    client.close()

if __name__ == "__main__":
    start_client()
