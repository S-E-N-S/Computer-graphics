from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtWidgets import QGraphicsItem, QGraphicsScene, QGraphicsView
from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout
from PySide2.QtGui import QPen, QBrush
from PySide2.QtCore import Qt  # for pen' colors
import numpy as np


WINDOW_HEIGHT = 600
WINDOW_WIDTH = 800
VIEW_HEIGHT = 300
VIEW_WIDTH = 400
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
        self._points = np.zeros([num, 2])
        # set X from 0 to 1
        step = float(1) / num
        # set Y -1 or 1 (avoid init with straight line)
        for i in range(num):
            self._points[i, 0] = i * step
            self._points[i, 1] = 1 if i % 2 == 0 else -1

    def _create_widgets(self):
        main_layout = QVBoxLayout(self)

        # create plot area
        self._scene = QGraphicsScene(self)
        self._view = QGraphicsView(self._scene, self)
        self._view.setFixedHeight(VIEW_HEIGHT)
        self._view.setFixedWidth(VIEW_WIDTH)
        main_layout.addWidget(self._view)

        self._plot_axis()

        # add everything to the window
        self.setLayout(main_layout)

    def _plot_axis(self):
        # create pen
        pen = QPen(Qt.blue)
        # X axis
        self._scene.addLine(-VIEW_WIDTH / 2, 0, VIEW_WIDTH / 2, 0, pen)
        # Y axis
        self._scene.addLine(0, -VIEW_HEIGHT / 2, 0, VIEW_HEIGHT / 2, pen)

    def _plot_bezier_lines(self, points_list):
        for points_seq in points_list:
            for i in range(len(points_seq) - 1):
                self._scene.addLine(points_seq[i][0], points_seq[i][1],
                                    points_seq[i + 1][0], points_seq[i + 1][1])



def entry_point():
    app = QApplication()
    window = SplineWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    entry_point()
