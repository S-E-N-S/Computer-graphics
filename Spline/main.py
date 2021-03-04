from PySide2.QtWidgets import QApplication, QMainWindow, QWidget
from PySide2.QtWidgets import QGraphicsItem, QGraphicsScene, QGraphicsView
from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout
from PySide2.QtGui import QPen, QBrush
from PySide2.QtCore import Qt  # for pen' colors
import numpy as np
from bezier_curve import BezierManager

WINDOW_HEIGHT = 600
WINDOW_WIDTH = 800
VIEW_HEIGHT = 300
VIEW_WIDTH = 400
X_LIM = 5
Y_LIM = 5
POINT_COUNT = 3


class SplineWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bezier Splines by S-E-N-S")
        self.setFixedWidth(WINDOW_WIDTH)
        self.setFixedHeight(WINDOW_HEIGHT)
        self._create_points(POINT_COUNT)
        self._create_widgets()

    def _create_points(self, num=3):
        self._points_cnt = num
        self._points = np.zeros([num, 2])
        # set X from 0 to 1
        step = float(1) / num
        # set Y -1 or 1 (avoid init with straight line)
        for i in range(num):
            self._points[i, 0] = i * step
            self._points[i, 1] = 1 if i % 2 == 0 else -1

    def _create_widgets(self):
        central_widget = QWidget(self)
        main_layout = QVBoxLayout(self)

        # init points
        self._create_points()
        # init Bezier Manager
        self._bezier_manager = BezierManager(self._points_cnt)
        self._bezier_manager.set_points(self._points)

        # create plot area
        self._scene = QGraphicsScene(self)
        self._view = QGraphicsView(self._scene, self)
        self._view.setFixedHeight(VIEW_HEIGHT)
        self._view.setFixedWidth(VIEW_WIDTH)
        main_layout.addWidget(self._view)

        # set scale
        self._x_scale = VIEW_WIDTH / X_LIM
        self._y_scale = VIEW_HEIGHT / Y_LIM

        self._plot_axis()
        # compute & plot bezier lines
        self._cur_t = 0.5
        points_list = self._bezier_manager.get_points(self._cur_t)
        self._plot_bezier_lines(points_list)
        self._plot_bezier_trace(self._cur_t)

        # add everything to the window
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def _plot_axis(self):
        # create pen
        pen = QPen(Qt.blue)
        # X axis
        self._add_line(-X_LIM / 2, 0, X_LIM / 2, 0, pen)
        # Y axis
        self._add_line(0, -X_LIM / 2, 0, X_LIM / 2, pen)

    def _plot_bezier_lines(self, points_list):
        # create pen
        pen = QPen(Qt.black)
        for points_seq in points_list:
            if len(points_seq) <= 1:
                # the last-level point
                break
            print("\n\n\n")
            for i in range(len(points_seq) - 1):
                self._add_line(points_seq[i][0], points_seq[i][1],
                               points_seq[i + 1][0], points_seq[i + 1][1], pen)

    def _plot_bezier_trace(self, current_t):
        pen = QPen(Qt.red)
        t_net = np.linspace(0, current_t)
        prev_point = self._bezier_manager.find_point(t_net[0])
        for k in range(1, len(t_net)):
            current_point = self._bezier_manager.find_point(t_net[k])
            self._add_line(prev_point[0], prev_point[1], current_point[0], current_point[1], pen)
            prev_point = current_point

    def _add_line(self, x1, y1, x2, y2, pen):
        # just add line but with scale
        self._scene.addLine(x1 * self._x_scale, y1 * self._y_scale,
                            x2 * self._x_scale, y2 * self._y_scale, pen)


def entry_point():
    app = QApplication()
    window = SplineWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    entry_point()
