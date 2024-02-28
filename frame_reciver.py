import socket
import threading
import struct

import os
import cv2
import numpy as np
from utilss import plot_one_box, cal_iou, xyxy_to_xywh, xywh_to_xyxy, updata_trace_list, draw_trace

import pickle

import time
import datetime

def charge_socket_recive_init():
    # 创建一个socket对象
    global charge_socket_recive
    charge_socket_recive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 获取本地主机名
    host = '127.0.0.1'
    print(host)
    port = 9999
    # 连接服务，指定主机和端口
    charge_socket_recive.connect((host, port))

     
def show_words():
    msg = charge_socket_recive.recv(1024)
    a = msg.decode('utf-8')
    print(f'{a}---{datetime.datetime.fromtimestamp(time.time())}')
                
if __name__ == '__main__':
    charge_socket_recive_init()
    
    data = b""
    payload_size = struct.calcsize("L")
    while True:
        # 从连接中接收数据
        while len(data) < payload_size:
            data += charge_socket_recive.recv(4096)
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("L", packed_msg_size)[0]
        # 保证接收到完整的数据
        while len(data) < msg_size:
            data += charge_socket_recive.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]
        # 解码图像帧
        frame = pickle.loads(frame_data)
        cv2.imshow('rtsp', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


        #show_words()
        
        #print(msg.decode('utf-8'))
        # 关闭连接
        #charge_socket_recive.close()
        #time.sleep(1)
