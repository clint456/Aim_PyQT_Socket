import pickle
import socket
import struct
import sys
import time

import numpy as np
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QThread, QObject, Signal, QMutex, QMutexLocker
from GUI_ui import Ui_Form  # 导入Qt Designer生成的UI文件
import cv2
# ================================================== 主窗口页面 =====================================================================
             
# 定义一些常量和状态
VIDEO_TYPE_OFFLINE = 0
VIDEO_TYPE_REAL_TIME = 1


# 定义主窗口类，继承自QMainWindow和UI文件生成的类
class MyMainWindow(QMainWindow, Ui_Form):

    def __init__(self, parent=None, video_url="", video_type=VIDEO_TYPE_OFFLINE, auto_play=True,socket_config = ["localhost",5555,"localhost",9999]):
        super().__init__()
        # socket初始化
        self.socket_address_receive = socket_config[0]
        self.socket_port_receive = socket_config[1]
        self.socket_address_send = socket_config[2]
        self.socket_port_send = socket_config[3]

        self.socket_send_flag =False
        self.socket_receive_flag =False

        # 视频源初始化
        self.video_type = video_type
        self.video_url = video_url
        self.video_type = video_type
        self.auto_play = auto_play

        self.is_switching = False
        self.is_pause = True

        # 开火位
        self.is_fire = 0
        # 位置、开火数据包
        self.pos_str = {'x':0,'y':0,'fire':0}


        # 初始化界面
        self.setupUi(self)


        # 设置提示文本的字体为微软雅黑，字号为12
        QToolTip.setFont(QFont('微软雅黑', 10))

        # 获取图片并调整大小
        init_image = QPixmap("resource/picture.png")
        init_image = init_image.scaled(self.pictureLabel.width(), self.pictureLabel.height(), Qt.KeepAspectRatio)
        self.pictureLabel.setPixmap(init_image)

        # 播放按钮
        self.playButton.setEnabled(True)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.switch_socket_video)

        control_box = QHBoxLayout()
        control_box.setContentsMargins(0, 0, 0, 0)
        control_box.addWidget(self.playButton)

        layout = QVBoxLayout()
        layout.addWidget(self.pictureLabel)
        layout.addLayout(control_box)
        self.setLayout(layout)

        # 定时器循环设置
        self.timer = VideoTimer()
        self.timer.timeSignal.signal[str].connect(self.show_video_images)

        # 视频初始设置
        self.playCapture = cv2.VideoCapture()
        if self.video_url != "":
            self.set_timer_fps()
            if self.auto_play:
                self.switch_socket_video()

        # 信号与槽
        self.CreateSignalSlot()
    # 创建信号与槽连接
    def CreateSignalSlot(self):
        self.pushButton_aim.clicked.connect(self.aim_handle)
        self.pushButton_shot.clicked.connect(self.shot_handle)

    def aim_handle(self):
        print("瞄准中")

        pass

    def shot_handle(self):
        if not self.is_fire:

            self.pushButton_shot.setText('停火')
            self.is_fire = 1



        elif self.is_fire:

            self.is_fire = 0
            self.pushButton_shot.setText('开火')

        pass
    # 鼠标点击事件
    def mousePressEvent(self, event):
        global_pos = event.globalPos()  
        local_pos = self.pictureLabel.mapFromGlobal(global_pos)
        if event.button() == Qt.LeftButton and self.pictureLabel.rect().contains(local_pos):
            print(f"鼠标点击:\n全局坐标：({global_pos.x()}, {global_pos.y()})")
            print(f"相对坐标：({local_pos.x()}, {local_pos.y()})")
        super(MyMainWindow, self).mousePressEvent(event)
        # Convert QPoint to a string representation
        self.pos_str = {'x':local_pos.x(),'y':local_pos.y(),'fire':self.is_fire}
        # 发送坐标数据
        pickle_data = pickle.dumps(self.pos_str)
        self.server_socket.send(pickle_data)



#   初始化 播放
    def reset(self):
        self.timer.stop()
        self.playCapture.release()
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

#   设置视频流输入方式
    def set_video(self, url, video_type=VIDEO_TYPE_OFFLINE, auto_play=True):
        self.reset()
        self.video_url = url
        self.video_type = video_type
        self.auto_play = auto_play
        if self.auto_play:
            self.switch_socket_video()


    """
    VIDEO_TYPE_OFFLINE = 0
    VIDEO_TYPE_REAL_TIME = 1
    """
    # 播放视频流
    def show_video_images(self):
        if self.video_type  == VIDEO_TYPE_OFFLINE:
            if self.playCapture.isOpened():
                success, frame = self.playCapture.read()
                if success:
                    height, width = frame.shape[:2]
                    if frame.ndim == 3:
                        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    elif frame.ndim == 2:
                        rgb = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

                    temp_image = QImage(rgb.flatten(), width, height, QImage.Format_RGB888)
                    temp_pixmap = QPixmap.fromImage(temp_image)
                    self.pictureLabel.setPixmap(temp_pixmap)

                else:
                    print("读取失败，无帧数据")
                    success, frame = self.playCapture.read()
                    if not success and self.video_type is VIDEO_TYPE_OFFLINE:
                        print("播放完成")
                        self.reset()
                        # 设置按键形状
                        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
                    return
            else:
                print("打开文件或捕获设备错误，重新初始化")
                self.reset()
        elif self.video_type is VIDEO_TYPE_REAL_TIME:
            self.udpStream_server()

    # mp4播放控制模块
    def switch_video(self):

        if self.video_url == "" or self.video_url is None:
            return
        if self.is_fire or self.is_switching:

            self.playCapture.open(self.video_url)

            self.timer.stop()

            self.is_pause = False
            self.playButton.setText('停止')
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        elif (not self.is_pause) and (not self.is_switching):

            self.timer.start()

            self.is_pause = True
            self.playButton.setText('运行')
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    #  socket播放视频控制模块
    def switch_socket_video(self):
        if self.video_type is VIDEO_TYPE_OFFLINE:
            self.switch_video()
        elif self.video_type is VIDEO_TYPE_REAL_TIME:
            if self.is_pause or self.is_switching:
                
                self.timer.start()
                print("视频帧获取定时器----开启")
                self.init_socket_receive_server()
                print("【接收图像】服务器---开启")
                self.init_socket_send_server()
                print("【发送坐标】客户端开启")
                

                self.is_pause = False
                self.playButton.setText('停止')
                self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
                # 接收socket线程启动 ，这里暂时不需要
                #threading.Thread(target=self.udpStream_server).start()
            elif (not self.is_pause) and (not self.is_switching):

                self.timer.stop()
                print("视频帧获取定时器---关闭")
                self.socket_client.close()
                print("【接收图像】服务器====关闭")
                self.server_socket.close()
                print("【发送坐标】客户端关闭")
                

                self.is_pause = True
                self.playButton.setText('运行')
                self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
                

    # socket服务器初始化
    def init_socket_receive_server(self):
# ============= 接收客户端初始化 ================================
        self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"Socket服务器已启动，监听端口：{self.socket_port_receive}")
        #设置非阻塞模式
        self.socket_client.bind(('0.0.0.0',5555))
        self.socket_client.setblocking(0)

        #self.socket_client.connect((self.socket_address_receive, self.socket_port_receive))
        #print("Socket【接收图像】服务器已连接")
        
        self.socket_send_flag = True

    def init_socket_send_server(self):
# ============= 发送客户端初始化 ================================
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Socket服务器已启动，监听端口：{self.socket_port_send}")
        try:
            self.server_socket.connect((self.socket_address_send, self.socket_port_send))
            print("Socket【发送坐标】客户端已连接")
        except Exception as e:
            print("发送坐标客户端初始化失败",e)
            return

    def udpStream_server(self):
        data = None
       # print("------------------视频流进入")
        try:
            data, _ = self.socket_client.recvfrom(921600)
            receive_data = np.frombuffer(data, dtype='uint8')
            r_img = cv2.imdecode(receive_data, 1)
            self.show_video_frame(r_img)
            #cv2.putText(r_img, "server", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.imshow('server', r_img)
            # cv2.putText(r_img, "server", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            # cv2.imshow('server', r_img)
        except BlockingIOError as e:
            pass

        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     self.timer.stop()
    # socket 视频接收
    def receive_video_from_socket(self):
        # try:
            size_data = self.socket_client.recv(4)
            size = struct.unpack('!I', size_data)[0]
            frame_data = self.socket_client.recv(size)
            # try:
            frame = pickle.loads(frame_data)
                #print(loaded_data)
            # except pickle.UnpicklingError as e:
            #     print(f"反序列化时出错：{e}")
            # 在这里你可以进行一些处理，例如显示帧
            self.show_video_frame(frame)

        # except Exception as e:
        #     print(f"接收视频时发生错误：{e}")

    # socket视频显示 -> qt
    def show_video_frame(self, frame):
        if frame is not None:
            height, width = frame.shape[:2]
            if frame.ndim == 3:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            elif frame.ndim == 2:
                rgb = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

            temp_image = QImage(rgb.flatten(), width, height, QImage.Format_RGB888)
            temp_pixmap = QPixmap.fromImage(temp_image)
            self.pictureLabel.setPixmap(temp_pixmap)
        else:
            print("未收到socket视频帧")
            self.reset()

# 用于线程间通信的信号类
class Communicate(QObject):
    signal = Signal(str)

# 视频定时器类
class VideoTimer(QThread):
    
    def __init__(self, frequent=200):
        QThread.__init__(self)
        self.stopped = False
        self.frequent = frequent
        self.timeSignal = Communicate()
        self.mutex = QMutex()

    # 死循环：每20ms刷新一次
    def run(self):
        with QMutexLocker(self.mutex):
            self.stopped = False
        while True:
            if self.stopped:
                return
            self.timeSignal.signal.emit("1")
            time.sleep(1 / self.frequent)

    def stop(self):
        with QMutexLocker(self.mutex):
            self.stopped = True


    """
    # 定义一些常量和状态
    VIDEO_TYPE_OFFLINE = 0
    VIDEO_TYPE_REAL_TIME = 1

    GUI/resource/video.mp4
    """
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyMainWindow(socket_config=["localhost",5555,"localhost",9999])
    myWin.set_video("",VIDEO_TYPE_REAL_TIME)
    myWin.show()
    sys.exit(app.exec())
