import pickle
import socket
import struct
import sys
import threading
import time

import numpy as np
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QThread, QObject, Signal, QMutex, QMutexLocker
from GUI_ui import Ui_Form  # 导入Qt Designer生成的UI文件
import cv2
from PySide6 import QtCore, QtGui, QtWidgets

# 定义一些常量和状态
VIDEO_TYPE_OFFLINE = 0
VIDEO_TYPE_REAL_TIME = 1
STATUS_INIT = 0
STATUS_PLAYING = 1
STATUS_PAUSE = 2

# 定义主窗口类，继承自QMainWindow和UI文件生成的类
class MyMainWindow(QMainWindow, Ui_Form):


    # def __init__(self, parent=None, video_url="", video_type=VIDEO_TYPE_OFFLINE, auto_play=True):
    #     super(MyMainWindow, self).__init__(parent)
    def __init__(self, parent=None, video_url="", video_type=VIDEO_TYPE_OFFLINE, auto_play=True,address = "localhost", port=9999):
        super().__init__()
        # socket初始化
        self.socket_port = port
        self.socket_adress = address
        self.video_type = video_type

        if self.video_type == VIDEO_TYPE_REAL_TIME:
            self.init_socket_server()

        self.video_url = video_url
        self.video_type = video_type
        self.auto_play = auto_play
        self.status = STATUS_INIT

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

        # 定时器设置
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

    # 鼠标点击事件
    def mousePressEvent(self, event):
        global_pos = event.globalPos()
        local_pos = self.pictureLabel.mapFromGlobal(global_pos)
        if event.button() == Qt.LeftButton and self.pictureLabel.rect().contains(local_pos):
            print(f"鼠标点击位置：({local_pos.x()}, {local_pos.y()})")
        super(MyMainWindow, self).mousePressEvent(event)

    # 创建信号与槽连接
    def CreateSignalSlot(self):
        self.pushButton_aim.clicked.connect(self.aim_handle)
        self.pushButton_shot.clicked.connect(self.shot_handle)

    def aim_handle(self):
        print("瞄准中")
        pass

    def shot_handle(self):
        print("射击")
        pass

    def reset(self):
        self.timer.stop()
        self.playCapture.release()
        self.status = STATUS_INIT
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def set_timer_fps(self):
        self.playCapture.open(self.video_url)
        # fps = self.playCapture.get(cv2.CAP_PROP_FPS)
        # print(f"帧率为：{fps}")
        # self.timer.set_fps(fps)
        self.playCapture.release()

    def set_video(self, url, video_type=VIDEO_TYPE_OFFLINE, auto_play=True):
        self.reset()
        self.video_url = url
        self.video_type = video_type
        self.auto_play = auto_play
        #self.set_timer_fps()
        if self.auto_play:
            self.switch_socket_video()

    def play(self):
        if self.video_url == "" or self.video_url is None:
            return
        if not self.playCapture.isOpened():
            self.playCapture.open(self.video_url)
        self.timer.start()
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.status = MyMainWindow.STATUS_PLAYING

    def stop(self):
        if self.video_url == "" or self.video_url is None:
            return
        if self.playCapture.isOpened():
            self.timer.stop()
            if self.video_type is VIDEO_TYPE_REAL_TIME:
                self.playCapture.release()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.status = MyMainWindow.STATUS_PAUSE

    def re_play(self):
        if self.video_url == "" or self.video_url is None:
            return
        self.playCapture.release()
        self.playCapture.open(self.video_url)
        self.timer.start()
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.status = MyMainWindow.STATUS_PLAYING

    """
    VIDEO_TYPE_OFFLINE = 0
    VIDEO_TYPE_REAL_TIME = 1
    STATUS_INIT = 0
    STATUS_PLAYING = 1
    STATUS_PAUSE = 2
    """
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
                        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
                    return
            else:
                print("打开文件或捕获设备错误，重新初始化")
                self.reset()
        elif self.video_type is VIDEO_TYPE_REAL_TIME:
            self.receive_video_from_socket()

############## 按键的逻辑有问题
    def switch_video(self):
        if self.video_url == "" or self.video_url is None:
            return
        if self.status is STATUS_INIT:
            self.playCapture.open(self.video_url)
            self.timer.start()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        elif self.status is STATUS_PLAYING:
            self.timer.stop()
            if self.video_type is VIDEO_TYPE_REAL_TIME:
                self.playCapture.release()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        elif self.status is STATUS_PAUSE:
            if self.video_type is VIDEO_TYPE_REAL_TIME:
                self.playCapture.open(self.video_url)
            self.timer.start()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

        self.status = (STATUS_PLAYING,
                       STATUS_PAUSE,
                       STATUS_PLAYING)[self.status]

    def switch_socket_video(self):
        if self.video_type is VIDEO_TYPE_OFFLINE:
            self.switch_video()
        elif self.video_type is VIDEO_TYPE_REAL_TIME:
            if self.status is STATUS_INIT:
                self.init_socket_server()
                self.timer.start()
                self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
                self.status = STATUS_PLAYING
                threading.Thread(target=self.receive_video_from_socket).start()
            elif self.status is STATUS_PLAYING:
                self.timer.stop()
                self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
                self.socket_client.close()
            elif self.status is STATUS_PAUSE:
                self.timer.start()
                self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
                self.status = STATUS_PLAYING
            self.status = (STATUS_PLAYING,
                           STATUS_PAUSE,
                           STATUS_PLAYING)[self.status]

    def init_socket_server(self):
        self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Socket服务器已启动，监听端口：{self.socket_port}")
        self.socket_client.connect((self.socket_adress, self.socket_port))
        print("Socket客户端已连接")

    def receive_video_from_socket(self):
        try:
            size_data = self.socket_client.recv(4)
            size = struct.unpack('!I', size_data)[0]
            frame_data = self.socket_client.recv(size)
            try:
                frame = pickle.loads(frame_data)
                #print(loaded_data)
            except pickle.UnpicklingError as e:
                print(f"反序列化时出错：{e}")
            # 在这里你可以进行一些处理，例如显示帧
            self.show_video_frame(frame)

        except Exception as e:
            print(f"接收视频时发生错误：{e}")

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
    def __init__(self, frequent=20):
        QThread.__init__(self)
        self.stopped = False
        self.frequent = frequent
        self.timeSignal = Communicate()
        self.mutex = QMutex()

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

    def is_stopped(self):
        with QMutexLocker(self.mutex):
            return self.stopped

    def set_fps(self, fps):
        self.frequent = fps


"""
# 定义一些常量和状态
VIDEO_TYPE_OFFLINE = 0
VIDEO_TYPE_REAL_TIME = 1
STATUS_INIT = 0
STATUS_PLAYING = 1
STATUS_PAUSE = 2
"""
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.set_video(" ",VIDEO_TYPE_REAL_TIME)
    myWin.show()
    sys.exit(app.exec_())