import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.lines as lines

start = '2015-01-01'
end = '2015-03-01'

df = pd.DataFrame(pd.date_range(start=start, end=end, freq='D'),
                                  columns=['time'])
df['data'] = np.random.randint(1, 10, len(df))


class HighlightSelected(lines.VertexSelector):
    def __init__(self, line, fmt='ro', **kwargs):
        lines.VertexSelector.__init__(self, line)
        self.markers, = self.axes.plot_date([], [], fmt, **kwargs)
        self.pos = []

    def process_selected(self, ind, xs, ys):
        self.markers.set_data(xs, ys)
        self.canvas.draw()

    def onpick(self, event):
        """When the line is picked, update the set of selected indicies."""
        if event.artist is not self.line:
            return

        thisline = event.artist
        xdata = thisline.get_xdata()
        ydata = thisline.get_ydata()
        print(event.ind)
        for i in event.ind:
            data = (xdata[i], ydata[i])
            if i in self.ind:
                self.ind.remove(i)
                self.pos.remove(data)
                print('removed: ', data)
                print(len(self.pos))
            else:
                self.ind.add(i)
                self.pos.append(data)
                print('added: ', data)
                print(len(self.pos))
        ind = list(self.ind)
        ind.sort()
        xdata, ydata = self.line.get_data()
        self.process_selected(ind, xdata[ind], ydata[ind])


def onpick(event):
    thisline = event.artist
    xdata = thisline.get_xdata()
    ydata = thisline.get_ydata()
    ind = event.ind
    print(xdata[ind], ydata[ind])

fig = plt.figure()
ax = fig.add_subplot(111)
line, = ax.plot_date(df.time, df.data, 'o', picker=5)

fig.canvas.mpl_connect('pick_event', onpick)
selector = HighlightSelected(line)
plt.show()
print('selector', selector.pos)