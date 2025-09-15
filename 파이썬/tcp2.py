import socket

def tcp_client():
    host = "127.0.0.1"
    port = 5000
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))   # 서버 연결
    
    message = input("보낼 메시지 입력: ")
    while message.lower() != "exit":
        client_socket.send(message.encode())
        data = client_socket.recv(1024).decode()
        print("서버 응답:", data)
        message = input("보낼 메시지 입력: ")
    
    client_socket.close()

if __name__ == "__main__":
    tcp_client()
