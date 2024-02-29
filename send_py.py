import cv2
import socket
import pickle
import struct

class VideoSender:
    def __init__(self, host='localhost', port = 5555):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(1)

        self.client_socket, addr = self.server_socket.accept()
        self.connection = self.client_socket.makefile('wb')

        self.cap = cv2.VideoCapture(0)

    def send_frames(self):
        while True:
            ret, frame = self.cap.read()
            data = pickle.dumps(frame)
            size = struct.pack('!I', len(data))
            self.connection.write(size)
            self.connection.write(data)

    def close(self):
        self.cap.release()
        self.connection.close()
        self.client_socket.close()
        self.server_socket.close()

if __name__ == "__main__":
    sender = VideoSender()
    sender.send_frames()
    sender.close()
