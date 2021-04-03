from PySide2.QtWidgets import QApplication, QMainWindow, QWidget
from PySide2.QtWidgets import QGraphicsScene, QGraphicsView
from PySide2.QtWidgets import QVBoxLayout, QGraphicsEllipseItem, QPushButton
from PySide2.QtGui import QPen, QBrush
from PySide2.QtCore import Qt, QTimer
import numpy as np
from bezier_curve import BezierManager
from MovableCircle import MovableCircle
from TSlider import TSlider
from PointSetter import PointSetter
from PySide2.QtGui import QCursor

WINDOW_HEIGHT = 800
WINDOW_WIDTH = 1300
VIEW_HEIGHT = 750
VIEW_WIDTH = 1250
POINT_COUNT = 4
POINTS_W = 15
POINTS_H = 15
# How many pixels are occupied by one
ONE_SCALE = 100
# the minimum number of points
POINTS_MIN_CNT = 3
# the maximum number of points
POINTS_MAX_CNT = 10
SLIDER_SCALE = 100
AX_TUNE = 30
DT_ANIMATION = 100


class SplineWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._init = False  # not initialized yet
        # colors for bezier support lines
        self._color_list = [
            Qt.black, Qt.blue, Qt.green,
            Qt.darkYellow, Qt.darkGreen,
            Qt.magenta, Qt.cyan
        ]
        self.setWindowTitle("Bezier Splines by S-E-N-S")
        self.setFixedWidth(WINDOW_WIDTH)
        self.setFixedHeight(WINDOW_HEIGHT)
        self._create_widgets()
        self.active_mode = False

    def mousePressEvent(self, event):
        if not self.active_mode:
            return

        pos = self._view.mapToScene(self._view.mapFromParent(event.pos()))

        points = list(self._points)
        points.append([pos.x(),
                       pos.y()])

        self._points = np.array(points)

        self._points_cnt += 1

        self._clear_prev_points()
        # init points
        self._bezier_manager.set_points(self._points)
        # create movable graphic items for Bezier points
        self._create_graphics_support_points()
        # draw everything
        self._redraw()
        self.active_mode = False
        if self.point_setter.can_unblock_plus():
            self.point_setter.button_plus.setEnabled(True)
        self.point_setter.button_minus.setEnabled(True)

    def _create_points(self, num=POINT_COUNT):
        self._points_cnt = num
        self._points = np.zeros([num, 2])
        # set X from 0 to 1
        step = float(1) / num
        # set Y -1 or 1 (avoid init with straight line)
        for i in range(num):
            # assign values to the points
            self._points[i, 0] = i * step * ONE_SCALE + VIEW_WIDTH / 2
            self._points[i, 1] = (1 if i % 2 == 0 else -1) * ONE_SCALE + VIEW_HEIGHT / 2

    def _create_graphics_support_points(self):
        self._point_items = []  # container for the points
        # init pen
        pen = QPen(Qt.black)
        # init brush
        brush = QBrush(Qt.green, Qt.SolidPattern)
        for i in range(self._points_cnt):
            # create graphics element
            new_item = MovableCircle(self,
                                     - POINTS_W / 2,
                                     - POINTS_H / 2,
                                     POINTS_W,
                                     POINTS_H,
                                     pen,
                                     brush,
                                     i,
                                     lambda point_idx, new_point: self._upd_point_coord(point_idx,
                                                                                        new_point.x(),
                                                                                        new_point.y()))
            new_item.setPos(self._points[i, 0], self._points[i, 1])
            self._scene.addItem(new_item)
            self._point_items.append(new_item)

    def _create_widgets(self):
        central_widget = QWidget(self)
        main_layout = QVBoxLayout(self)

        # init Bezier Manager
        self._bezier_manager = BezierManager()

        self._temporary_lines = []  # storage for the lines on the screen
        self._bezier_lines = []
        # add point that will represent the current point of the line corresponds to t parameter
        self._bezier_point = QGraphicsEllipseItem(0, 0, POINTS_W, POINTS_H)
        self._bezier_point.setPen(QPen(Qt.red))
        self._bezier_point.setBrush(QBrush(Qt.red, Qt.SolidPattern))

        # create plot area
        self._scene = QGraphicsScene(self)
        self._scene.addItem(self._bezier_point)
        self._view = QGraphicsView(self._scene, self)
        self._view.setFixedHeight(VIEW_HEIGHT)
        self._view.setFixedWidth(VIEW_WIDTH)
        main_layout.addWidget(self._view)

        self._create_and_draw_points(POINT_COUNT)

        # add everything to the window
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        slider_obj = self.slider = TSlider(lambda value: self.change_t_value(value), self._cur_t * 100, SLIDER_SCALE)
        self._scene.addWidget(self.slider)
        self.slider.add_text(SplineWindow._to_fixed(self._cur_t, 2))

        # define callbacks for point change buttons
        def inc_callback():
            self.active_mode = True
            self._view.viewport().setCursor(Qt.CursorShape.CrossCursor)

        def dec_callback():
            points = list(self._points)
            points.pop()
            self._points = np.array(points)

            self._points_cnt -= 1

            self._clear_prev_points()
            # init points
            self._bezier_manager.set_points(self._points)
            # create movable graphic items for Bezier points
            self._create_graphics_support_points()
            # draw everything
            self._redraw()

        self.point_setter = PointSetter(inc_callback, dec_callback, self._points_cnt,
                                        POINTS_MIN_CNT, POINTS_MAX_CNT)
        self.point_setter.setFixedWidth(slider_obj.width())
        point_setter_obj = self._scene.addWidget(self.point_setter)
        point_setter_obj.setPos(0, slider_obj.height())

        # add animation button
        self._play_button = QPushButton("Play")
        self._play_active = False
        self._play_timer = QTimer()
        self._play_timer.setInterval(DT_ANIMATION)
        self._play_direction = 1

        def play_timer_slot():
            dt = 0.05
            self._cur_t += dt * self._play_direction
            if self._cur_t >= 1:
                self._cur_t = 1
                self._play_direction = -self._play_direction
            if self._cur_t <= 0:
                self._cur_t = 0
                self._play_direction = -self._play_direction
            self._redraw()
            self.slider.set_value_float(self._cur_t)
            self.slider.add_text(SplineWindow._to_fixed(self._cur_t, 2))

        self._play_timer.timeout.connect(play_timer_slot)

        def play_button_slot():
            self._play_active = not self._play_active
            if self._play_active:
                self._play_button.setText("Stop")
                self._play_timer.start()
            else:
                self._play_button.setText("Play")
                self._play_timer.stop()

        self._play_button.clicked.connect(play_button_slot)

        play_button_obj = self._scene.addWidget(self._play_button)
        play_button_obj.setPos(slider_obj.width(), 0)

    def _add_and_draw_points(self, points_count):
        self._bezier_manager.set_points(self._points)
        # create movable graphic items for Bezier points
        self._create_graphics_support_points()
        # compute & plot bezier lines
        self._cur_t = 1
        # draw everything
        self._redraw()  # draw support lines

    def _create_and_draw_points(self, points_count):
        # (when we want to redraw lines, we have to delete the previous lines)
        self._clear_prev_points()
        # init points
        self._create_points(points_count)
        self._bezier_manager.set_points(self._points)
        # create movable graphic items for Bezier points
        self._create_graphics_support_points()
        # compute & plot bezier lines
        self._cur_t = 1
        # draw everything
        self._redraw()  # draw support lines

    def _clear_prev_points(self):
        if not self._init:
            # don't need to clear for the first time
            self._init = True
            return
        for cur_line in self._temporary_lines:
            self._scene.removeItem(cur_line)
        for cur_line in self._bezier_lines:
            self._scene.removeItem(cur_line)
        for cur_movable_point in self._point_items:
            self._scene.removeItem(cur_movable_point)
        self._temporary_lines.clear()
        self._bezier_lines.clear()
        #self._point_items.clear()

    def change_t_value(self, value):
        self._cur_t = float(value) / (SLIDER_SCALE - 1)
        self._redraw()
        self.slider.add_text(SplineWindow._to_fixed(self._cur_t, 2))

    @staticmethod
    def _to_fixed(num_obj, digits=0):
        return f"{num_obj:.{digits}f}"

    def _plot_axis(self):
        # create pen
        pen = QPen(Qt.blue)
        # X axis
        self._scene.addLine(AX_TUNE, VIEW_HEIGHT / 2, VIEW_WIDTH - AX_TUNE, VIEW_HEIGHT / 2, pen)
        # Y axis
        self._scene.addLine(VIEW_WIDTH / 2, AX_TUNE, VIEW_WIDTH / 2, VIEW_HEIGHT - AX_TUNE, pen)

    def _plot_bezier_lines(self, points_list):
        # create pen
        line_width = 2
        pen = QPen(Qt.black, line_width, Qt.DotLine)
        for line_order_num, points_seq in enumerate(points_list):
            if len(points_seq) <= 1:
                # the last-level point
                break
            # change color for the next support lines
            pen.setColor(self._color_list[line_order_num % len(self._color_list)])
            for i in range(len(points_seq) - 1):
                self._add_line(points_seq[i][0], points_seq[i][1],
                               points_seq[i + 1][0], points_seq[i + 1][1], pen)

    def _plot_bezier_trace(self):
        # create pen
        line_width = 3
        pen = QPen(Qt.red, line_width, Qt.SolidLine)
        t_net = np.linspace(0, 1, num=100)
        prev_point = self._bezier_manager.find_point(t_net[0])
        for k in range(1, len(t_net)):
            current_point = self._bezier_manager.find_point(t_net[k])
            self._add_bezier_line(prev_point[0], prev_point[1], current_point[0], current_point[1], pen)
            prev_point = current_point

    def _move_bezier_point(self):
        cur_point = self._bezier_manager.find_point(self._cur_t)
        self._bezier_point.setPos(cur_point[0] - POINTS_W / 2,
                                  cur_point[1] - POINTS_H / 2)

    def _add_bezier_line(self, x1, y1, x2, y2, pen):
        # just add line but with scale
        cur_line = self._scene.addLine(x1, y1, x2, y2, pen)
        self._bezier_lines.append(cur_line)

    def _add_line(self, x1, y1, x2, y2, pen):
        # just add line but with scale
        cur_line = self._scene.addLine(x1, y1, x2, y2, pen)
        self._temporary_lines.append(cur_line)

    def _update_lines(self, points_list):
        line_num = 0
        for points_seq in points_list:
            if len(points_seq) <= 1:
                # the last-level point
                break
            for i in range(len(points_seq) - 1):
                self._temporary_lines[line_num].setLine(points_seq[i][0], points_seq[i][1],
                                                        points_seq[i + 1][0], points_seq[i + 1][1])
                line_num += 1

    def _update_bezier_lines(self):
        t_net = np.linspace(0, 1, num=100)
        prev_point = self._bezier_manager.find_point(t_net[0])
        for k in range(1, len(t_net)):
            current_point = self._bezier_manager.find_point(t_net[k])
            self._bezier_lines[k - 1].setLine(prev_point[0], prev_point[1], current_point[0], current_point[1])
            prev_point = current_point

    def _update_points(self):
        for i, point in enumerate(self._point_items):
            point.setPos(self._points[i, 0], self._points[i, 1])

    def _redraw(self):
        self._plot_axis()  # draw OX, OY
        # Compute Bezier support lines
        points_list = self._bezier_manager.get_points(self._cur_t)

        # init or update
        if len(self._temporary_lines) == 0:
            self._plot_bezier_lines(points_list)
        else:
            self._update_lines(points_list)

        # init or update
        if len(self._bezier_lines) == 0:
            self._plot_bezier_trace()
        else:
            self._update_bezier_lines()

        self._move_bezier_point()

        self._update_points()

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
