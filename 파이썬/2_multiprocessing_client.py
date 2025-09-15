import socket

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("127.0.0.1", 5000))  # 로컬 서버에 접속
    print("[서버 연결 완료]")

    try:
        while True:
            msg = input("보낼 메시지: ")
            if msg.lower() == "exit":
                break
            client_socket.sendall(msg.encode())
            data = client_socket.recv(1024)
            print(f"[서버 응답] {data.decode()}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()
