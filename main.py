import socket
import cv2
import time
from multiprocessing import Process


def gui():  # will be used for setting up a gui
    pass


def com_server():  # pure low-level communication with server (on raspberry)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 9090))
    while True:
        client_socket.send(b'imag ')
        data = client_socket.recv(60000)
        print(data)
        time.sleep(0.06)


if __name__ == '__main__':
    p_ser = Process(target=com_server())
    p_ser.start()
