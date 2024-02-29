import socket

# 创建一个 socket 对象
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 连接到服务器
host = '127.0.0.1'
port = 9999
client_socket.connect((host, port))

while True:
    # 输入要发送的数据
    message = input("Enter message to send (or 'exit' to quit): ")
    
    if message.lower() == 'exit':
        break
    
    # 发送数据
    client_socket.send(message.encode('utf-8'))

# 关闭连接
client_socket.close()
