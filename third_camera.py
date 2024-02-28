#coding=utf-8
import cv2
import numpy as np
import mvsdk
import platform
import datetime
import time
import torch
from ultralytics import YOLO
import socket
import pickle
import struct
import imutils

def socket_framesend_init():
    global frame_socket,frame_addr    
    # 创建一个socket对象
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 获取本地主机名
    host = '127.0.0.1'
    port = 9999
    # 绑定端口
    server_socket.bind((host, port))
    # 设置最大连接数，超过后排队
    server_socket.listen(5)
    # 建立客户端连接
    frame_socket, frame_addr = server_socket.accept()
    print('连接地址：', frame_addr)

    
def main_loop():
	socket_framesend_init()
	print('等待连接')
	# 枚举相机
	DevList = mvsdk.CameraEnumerateDevice()
	nDev = len(DevList)
	if nDev < 1:
		print("No camera was found!")
		return

	for i, DevInfo in enumerate(DevList):
		print("{}: {} {}".format(i, DevInfo.GetFriendlyName(), DevInfo.GetPortType()))
	i = 0 if nDev == 1 else int(input("Select camera: "))
	DevInfo = DevList[i]
	print(DevInfo)

	# 打开相机
	hCamera = 0
	try:
		hCamera = mvsdk.CameraInit(DevInfo, -1, -1)
	except mvsdk.CameraException as e:
		print("CameraInit Failed({}): {}".format(e.error_code, e.message) )
		return

	# 获取相机特性描述
	cap = mvsdk.CameraGetCapability(hCamera)

	# 判断是黑白相机还是彩色相机
	monoCamera = (cap.sIspCapacity.bMonoSensor != 0)

	# 黑白相机让ISP直接输出MONO数据，而不是扩展成R=G=B的24位灰度
	if monoCamera:
		mvsdk.CameraSetIspOutFormat(hCamera, mvsdk.CAMERA_MEDIA_TYPE_MONO8)
	else:
		mvsdk.CameraSetIspOutFormat(hCamera, mvsdk.CAMERA_MEDIA_TYPE_BGR8)

	# 相机模式切换成连续采集
	mvsdk.CameraSetTriggerMode(hCamera, 0)

	# 手动曝光，曝光时间30ms
	mvsdk.CameraSetAeState(hCamera, 0)
	mvsdk.CameraSetExposureTime(hCamera, 10 * 1000)
 
	# 增益
	mvsdk.CameraSetAnalogGain(hCamera,16)

	# 让SDK内部取图线程开始工作
	mvsdk.CameraPlay(hCamera)

	# 计算RGB buffer所需的大小，这里直接按照相机的最大分辨率来分配
	FrameBufferSize = cap.sResolutionRange.iWidthMax * cap.sResolutionRange.iHeightMax * (1 if monoCamera else 3)

	# 分配RGB buffer，用来存放ISP输出的图像
	# 备注：从相机传输到PC端的是RAW数据，在PC端通过软件ISP转为RGB数据（如果是黑白相机就不需要转换格式，但是ISP还有其它处理，所以也需要分配这个buffer）
	pFrameBuffer = mvsdk.CameraAlignMalloc(FrameBufferSize, 16)

	'''# 加载模型yolov5s 
	model = YOLO('yolov5s.pt')
	classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
"traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
"dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
"handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
"baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
"fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
"carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
"diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
"microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
"teddy bear", "hair drier", "toothbrush"]'''

	while (cv2.waitKey(1) & 0xFF) != ord('q'):
		# 从相机取一帧图片
		try:
			a = datetime.datetime.fromtimestamp(time.time()).timestamp()
			print(f'1---{datetime.datetime.fromtimestamp(time.time())}')
   
			pRawData, FrameHead = mvsdk.CameraGetImageBuffer(hCamera, 200)
			mvsdk.CameraImageProcess(hCamera, pRawData, pFrameBuffer, FrameHead)
			mvsdk.CameraReleaseImageBuffer(hCamera, pRawData)

			# windows下取到的图像数据是上下颠倒的，以BMP格式存放。转换成opencv则需要上下翻转成正的
			# linux下直接输出正的，不需要上下翻转
			if platform.system() == "Windows":
				mvsdk.CameraFlipFrameBuffer(pFrameBuffer, FrameHead, 1)
			
			# 此时图片已经存储在pFrameBuffer中，对于彩色相机pFrameBuffer=RGB数据，黑白相机pFrameBuffer=8位灰度数据
			# 把pFrameBuffer转换成opencv的图像格式以进行后续算法处理
			frame_data = (mvsdk.c_ubyte * FrameHead.uBytes).from_address(pFrameBuffer)
			frame = np.frombuffer(frame_data, dtype=np.uint8)
			frame = frame.reshape((FrameHead.iHeight, FrameHead.iWidth, 1 if FrameHead.uiMediaType == mvsdk.CAMERA_MEDIA_TYPE_MONO8 else 3) )
			
			if frame.shape[-1] == 1:
				frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			frame = cv2.resize(frame, (640, 480), interpolation = cv2.INTER_LINEAR)
			
			'''results = model(frame, stream=True)
			for result in results:
				for box in result.boxes:
					x1, y1, x2, y2 = box.xyxy[0]
					x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
					cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)
					cv2.putText(frame,
                 				classNames[int(box.cls[0])],
								(x1, y1),
								cv2.FONT_HERSHEY_SIMPLEX,
								1,(255,0,0),2)'''
			# Convert frame to bytes


			frame = imutils.resize(frame, width=800,height=576)  # 调整图像大小
			data = pickle.dumps(frame)
			message_size = struct.pack("L", len(data))
			frame_socket.sendall(message_size + data)
   
			b = datetime.datetime.fromtimestamp(time.time()).timestamp()
			print(f'2---{datetime.datetime.fromtimestamp(time.time())}') 

			fps = f'FPS={round(1/(b-a))}'
			cv2.putText(frame,fps,(0,20), cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2)

			cv2.imshow("Press q to end", frame)

			print(f'3---{datetime.datetime.fromtimestamp(time.time())}\n')

		except mvsdk.CameraException as e:
			if e.error_code != mvsdk.CAMERA_STATUS_TIME_OUT:
				print("CameraGetImageBuffer failed({}): {}".format(e.error_code, e.message) )

	# 关闭相机
	mvsdk.CameraUnInit(hCamera)

	# 释放帧缓存
	mvsdk.CameraAlignFree(pFrameBuffer)

def main():
	try:
		main_loop()
	finally:
		print('结束')
		cv2.destroyAllWindows()

main()
