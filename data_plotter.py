import socket, matplotlib, pickle
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import time

current_milli_time = lambda: int(round(time.time() * 1000))

style.use('fivethirtyeight')

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", 3303)) #For receiving command data

x = []

while True:
    data = pickle.loads(sock.recv(2048))
    print(data["raw_wave"])
    x.append(current_milli_time)
    y.append(data["raw_wave"])

    x = x[-50:]
    y = y[-50:]
    ax1.clear()
    ax1.plot(x, y)
