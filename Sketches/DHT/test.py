import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random

fig = plt.figure(figsize=(6,4))
axes = fig.add_subplot(1,1,1)
plt.title("Dynamic Axes")

y1 = [random.randint(-10,10)+(i**1.6)/(random.randint(9,12)) for i in range(0,280,2)]
t = range(len(y1))
x,y=[], []

def animate(i):
    x.append(t[i])
    y.append((y1[i]))
    plt.xlim(i-30,i+3)
    axes.set_ylim(y1[i]-100, y1[i]+100)
    plt.plot(x,y, scaley=True, scalex=True, color="red")

anim = FuncAnimation(fig, animate, interval=100)
plt.show()