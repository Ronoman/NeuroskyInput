import socket, matplotlib, pickle

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", 3303)) #For receiving command data

while True:
    data = pickle.loads(sock.recv(2048))
    print(data)
