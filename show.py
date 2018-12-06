import matplotlib.pyplot as plt
import matplotlib.animation as animation
fig = plt.figure()
    
def animate(i):
    ftemp = 'data.csv'
    fh = open(ftemp)
    x = []
    y = []
    for line in fh:
        pieces = line.split(',')
        time = pieces[0]
        muscle = pieces[1]
        x.append(time)
        y.append(muscle)
        #print(x,y)
        ax1 = fig.add_subplot(1,1,1,axisbg='white')
        ax1.clear()
        ax1.plot(x,y)
        
ani = animation.FuncAnimation(fig,animate,interval = 1000)
plt.show()