import socket

def udp_server():
    host = "127.0.0.1"
    port = 6000
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    
    print(f"UDP 서버 실행 중... (포트 {port})")
    
    while True:
        data, addr = server_socket.recvfrom(1024)
        print("클라이언트 메시지:", data.decode())
        server_socket.sendto(f"서버 응답: {data.decode()}".encode(), addr)

if __name__ == "__main__":
    udp_server()
