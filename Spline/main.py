from PySide2.QtWidgets import QApplication, QMainWindow, QWidget
from PySide2.QtWidgets import QGraphicsScene, QGraphicsView
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtGui import QPen, QBrush
from PySide2.QtCore import Qt  # for pen' colors
import numpy as np
from bezier_curve import BezierManager
from MovableCircle import MovableCircle
from TSlider import TSlider


WINDOW_HEIGHT = 600
WINDOW_WIDTH = 800
VIEW_HEIGHT = 500
VIEW_WIDTH = 700
POINT_COUNT = 4
POINTS_W = 10
POINTS_H = 10
# How many pixels are occupied by one
ONE_SCALE = 100


class SplineWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bezier Splines by S-E-N-S")
        self.setFixedWidth(WINDOW_WIDTH)
        self.setFixedHeight(WINDOW_HEIGHT)
        self._create_widgets()

    def _create_points(self, num=POINT_COUNT):
        self._points_cnt = num
        self._points = np.zeros([num, 2])
        # set X from 0 to 1
        step = float(1) / num
        # set Y -1 or 1 (avoid init with straight line)
        for i in range(num):
            # assign values to the points
            self._points[i, 0] = i * step * ONE_SCALE + VIEW_WIDTH/2
            self._points[i, 1] = (1 if i % 2 == 0 else -1) * ONE_SCALE + VIEW_HEIGHT/2

    def _create_graphics_support_points(self):
        self._point_items = []  # container for the points
        # init pen
        pen = QPen(Qt.black)
        # init brush
        brush = QBrush(Qt.green, Qt.SolidPattern)
        for i in range(self._points_cnt):
            # create graphics element
            new_item = MovableCircle(self,
                                     - POINTS_W/2,
                                     - POINTS_H/2,
                                     POINTS_W,
                                     POINTS_H,
                                     pen,
                                     brush,
                                     i,
                                     lambda point_idx, new_point: self._upd_point_coord(point_idx,
                                                                                        new_point.x(),
                                                                                        new_point.y()))
            new_item.setPos( self._points[i, 0],self._points[i, 1])
            self._scene.addItem(new_item)
            self._point_items.append(new_item)

    def _create_widgets(self):
        central_widget = QWidget(self)
        main_layout = QVBoxLayout(self)

        # init points
        self._create_points(POINT_COUNT)
        # init Bezier Manager
        self._bezier_manager = BezierManager()
        self._bezier_manager.set_points(self._points)

        # create plot area
        self._scene = QGraphicsScene(self)
        self._view = QGraphicsView(self._scene, self)
        self._view.setFixedHeight(VIEW_HEIGHT)
        self._view.setFixedWidth(VIEW_WIDTH)
        main_layout.addWidget(self._view)

        # create movable graphic items for Bezier points
        self._create_graphics_support_points()

        # compute & plot bezier lines
        self._cur_t = 1
        # draw everything
        self._temporary_lines = []  # storage for the lines on the screen
        self._bezier_lines = []
        # (when we want to redraw lines, we have to delete the previous lines)
        self._redraw()  # draw support lines

        # add everything to the window
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.slider = TSlider(lambda value:self.changeValue(value),self._cur_t*100 )
        self._scene.addWidget(self.slider)
        self.slider._add_text(self.toFixed(self._cur_t,2))


    def changeValue(self, value):
        self._cur_t = float(value)/99
        self._redraw()
        self.slider._add_text(self.toFixed(self._cur_t, 2))

    def toFixed(self,numObj, digits=0):
        return f"{numObj:.{digits}f}"

    def _plot_axis(self):
        # create pen
        pen = QPen(Qt.blue)
        # X axis
        self._scene.addLine(0, VIEW_HEIGHT/2, VIEW_WIDTH, VIEW_HEIGHT/2, pen)
        # Y axis
        self._scene.addLine(VIEW_WIDTH/2, 0, VIEW_WIDTH/2, VIEW_HEIGHT, pen)

    def _plot_bezier_lines(self, points_list):
        # create pen
        line_width = 3
        pen = QPen(Qt.black, line_width, Qt.DashLine)
        for points_seq in points_list:
            if len(points_seq) <= 1:
                # the last-level point
                break
            for i in range(len(points_seq) - 1):
                self._add_line(points_seq[i][0], points_seq[i][1],
                               points_seq[i + 1][0], points_seq[i + 1][1], pen)

    def _plot_bezier_trace(self):
        pen = QPen(Qt.red, 3, Qt.SolidLine)
        t_net = np.linspace(0, self._cur_t, num=100)
        prev_point = self._bezier_manager.find_point(t_net[0])
        for k in range(1, len(t_net)):
            current_point = self._bezier_manager.find_point(t_net[k])
            self._add_bezier_line(prev_point[0], prev_point[1], current_point[0], current_point[1], pen)
            prev_point = current_point

    def _add_bezier_line(self, x1, y1, x2, y2, pen):
        # just add line but with scale
        cur_line = self._scene.addLine(x1, y1, x2, y2, pen)
        self._bezier_lines.append(cur_line)

    def _add_line(self, x1, y1, x2, y2, pen):
        # just add line but with scale
        cur_line = self._scene.addLine(x1, y1, x2, y2, pen)
        self._temporary_lines.append(cur_line)

    def _update_lines(self, points_list):
        j=0
        for points_seq in points_list:
            if len(points_seq) <= 1:
                # the last-level point
                break
            for i in range(len(points_seq) - 1):
                self._temporary_lines[j].setLine(points_seq[i][0], points_seq[i][1],
                                                 points_seq[i+1][0], points_seq[i+1][1])
                j+=1

    def _update_bezier_lines(self, points_list):
        t_net = np.linspace(0, self._cur_t, num=100)
        prev_point = self._bezier_manager.find_point(t_net[0])
        for k in range(1, len(t_net)):
            current_point = self._bezier_manager.find_point(t_net[k])
            self._bezier_lines[k-1].setLine(prev_point[0], prev_point[1], current_point[0], current_point[1])
            prev_point = current_point

    def _redraw(self):
        # remove all old unneeded items (old lines)

            # self._scene.removeItem(current_item)
        self._plot_axis()  # draw OX, OY
        # Compute Bezier support lines
        points_list = self._bezier_manager.get_points(self._cur_t)

        if len(self._temporary_lines) == 0:
            self._plot_bezier_lines(points_list)
        else:
            self._update_lines(points_list)

        if len(self._bezier_lines)==0:
            self._plot_bezier_trace()
        else:
            self._update_bezier_lines(points_list)
        

        # Plot lines
        ## self._plot_bezier_lines(points_list)
        # Plot trace (Bezier curve for t < cur_t)
        # self._plot_bezier_trace()

    def _upd_point_coord(self, point_idx, new_x, new_y):
        # NOTE: new_x and new_y are scaled (they came as event.pos())
        # so we need to 'unscale' them
        # update coordinates in array
        self._points[point_idx, 0] = new_x
        self._points[point_idx, 1] = new_y
        # redraw lines
        self._redraw()


def entry_point():
    app = QApplication()
    window = SplineWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    entry_point()
