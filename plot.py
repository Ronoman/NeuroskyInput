import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

style.use('fivethirtyeight')

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

def animate(i):
    x = [1, 2, 3, 4, 5]
    y = [2, 5, 8, 2, 5]

    ax1.clear()
    ax1.plot(x, y)


ani = animation.FuncAnimation(fig, animate, interval=100)
plt.show()
