import socket
import time



for i in range(10):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('192.168.1.146', 8080))
    client_socket.send(b'image ')
    data = client_socket.recv(3)
    size = int.from_bytes(data, 'big')
    data = b''
    while len(data) < size:
        data += client_socket.recv(1024)


    # queue_img.put(data)
    img = open('img.jpg', 'wb')
    print(len(data))
    img.write(data)
    img.close()
    # break
    time.sleep(0.03)
