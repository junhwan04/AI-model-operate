import socket

def udp_client():
    host = "127.0.0.1"
    port = 6000
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    message = input("보낼 메시지 입력: ")
    while message.lower() != "exit":
        client_socket.sendto(message.encode(), (host, port))
        data, server = client_socket.recvfrom(1024)
        print("서버 응답:", data.decode())
        message = input("보낼 메시지 입력: ")
    
    client_socket.close()

if __name__ == "__main__":
    udp_client()
