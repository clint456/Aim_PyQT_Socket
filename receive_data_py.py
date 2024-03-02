import pickle
import select
import socket
import threading

def handle_client(client_socket):
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        try:
            received_data = pickle.loads(data)
            print("Received data:", received_data)
        except pickle.UnpicklingError as e:
            print("Error unpickling data:", e)

    print(f"Connection from {client_socket.getpeername()} closed.")
    client_socket.close()

# 创建一个 socket 对象
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 绑定地址和端口
host = 'localhost'
port = 9999
server_socket.bind((host, port))

# 监听连接
server_socket.listen(5)
print(f"Server listening on {host}:{port}")

# 用于存储待读取的sockets
inputs = [server_socket]

while True:
    # 使用select等待可读的socket
    readable, _, _ = select.select(inputs, [], [])

    for s in readable:
        if s is server_socket:
            # 有新连接
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")

            # 将新连接的socket加入待读取的列表
            inputs.append(client_socket)

            # 为每个连接创建一个新线程
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()
        else:
            # 有数据可读
            data = s.recv(1024)
            # 解析 pickle 包


            if not data:
                # 客户端断开连接
                print(f"Connection from {s.getpeername()} closed.")
                inputs.remove(s)
                s.close()
            else:
                # 打印接收到的数据
                try:
                    received_data = pickle.loads(data)
                    print("Received data:", received_data)
                except pickle.UnpicklingError as e:
                    print("Error unpickling data:", e)
