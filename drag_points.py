
import math
import matplotlib.lines as lines
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseEvent
from matplotlib.patches import Polygon


class DraggablePlotExample(object):
    u""" An example of plot with draggable markers """

    def __init__(self):
        self._figure, self._axes, self._line = None, None, None
        self._dragging_point = None
        self._points = {}

        self._init_plot()

    def _init_plot(self):
        self._figure = plt.figure("Example plot")
        axes = plt.subplot(1, 1, 1)
        axes.set_xlim(0, 100)
        axes.set_ylim(0, 100)
        axes.grid(which="both")
        self._axes = axes
        x = [0, 20, 10, 60, 80, 100]
        y = [60, 80, 20, 20, 80, 60]

        # Create dico ordonne
        for idx in range(len(x)):
            self._points[idx] = {}
            self._points[idx][x[idx]] = y[idx]
        print("self._points = ", self._points)

        print(dir(lines))
        self._line= lines.Line2D(x, y, mfc='red', ms=12, label='line label')
        self._axes.add_line(self._line)
        # self._line, = self._axes.plot(x, y, marker="o", markeredgecolor="blue", markerfacecolor="blue")

        self._figure.canvas.mpl_connect('button_press_event', self._on_click)
        self._figure.canvas.mpl_connect('button_release_event', self._on_release)
        self._figure.canvas.mpl_connect('motion_notify_event', self._on_motion)
        plt.show()

    def _update_plot(self):
        print("function _update_plot")
        if not self._points:
            self._line.set_data([], [])
        else:
            # x, y = zip(*sorted(self._points.items()))
            x = []
            y = []
            for key in sorted(self._points.keys()):
                print("--> key =", key)
                print("--> self._points[key] =", self._points[key])
                # input("wait...")
                x_, y_ = zip(*self._points[key].items())
                x.append(x_)
                y.append(y_)
            print(x, y)
            # Add new plot
            # if not self._line:
            #     self._line, = self._axes.plot(x, y, "b", marker="o", markersize=10)
            # # Update current plot
            # else:
            self._line.set_data(x, y)
        self._figure.canvas.draw()
        # input("wait...")

    def _add_point(self, x, y=None):
        print("add point")
        if isinstance(x, MouseEvent):
            x, y = int(x.xdata), int(x.ydata)

            self._points[self._dragging_key] = {}
            self._points[self._dragging_key][x] = y
            print("modify key = ", self._dragging_key)
            return x, y

    def _remove_point(self, x, _):
        print("remove point")
        if x in self._points[self._dragging_key]:
            self._points[self._dragging_key].pop(x)

    def _find_neighbor_point(self, event):
        u""" Find point around mouse position
        :rtype: ((int, int)|None)
        :return: (x, y) if there are any point around mouse else None
        """
        print("find nearest")
        distance_threshold = 3.0
        nearest_point = None
        min_distance = math.sqrt(2 * (100 ** 2))
        for key in self._points.keys():
            for x, y in self._points[key].items():
                distance = math.hypot(event.xdata - x, event.ydata - y)
                if distance < min_distance:
                    min_distance = distance
                    nearest_point = (x, y)
                    if min_distance < distance_threshold:
                        return key, nearest_point
        return None

    def _on_click(self, event):
        u""" callback method for mouse click event
        :type event: MouseEvent
        """
        # left click
        if event.button == 1 and event.inaxes in [self._axes]:
            key, point = self._find_neighbor_point(event)
            print("on_click, point = ", key, point)
            if point:
                print("key found = ", key)
                self._dragging_point = point
                self._dragging_key = key
            # else:
            #     self._add_point(event)
            self._update_plot()
        # right click
        # elif event.button == 3 and event.inaxes in [self._axes]:
        #     point = self._find_neighbor_point(event)
        #     if point:
        #         self._remove_point(*point)
        #         self._update_plot()

    def _on_release(self, event):
        u""" callback method for mouse release event
        :type event: MouseEvent
        """
        if event.button == 1 and event.inaxes in [self._axes] and self._dragging_point:
            self._dragging_point = None
            self._update_plot()

    def _on_motion(self, event):
        u""" callback method for mouse motion event
        :type event: MouseEvent
        """

        if not self._dragging_point:
            return
        if event.xdata is None or event.ydata is None:
            return
        self._remove_point(*self._dragging_point)
        self._dragging_point = self._add_point(event)
        self._update_plot()


if __name__ == "__main__":
    plot = DraggablePlotExample()