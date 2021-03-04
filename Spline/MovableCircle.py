from PySide2.QtWidgets import QApplication, QMainWindow, QWidget
from PySide2.QtWidgets import QGraphicsItem, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem
from PySide2.QtGui import QCursor
from PySide2.QtCore import Qt  # for cursor shapes
from PySide2.QtCore import QObject, Signal, Slot


class MovableCircle(QGraphicsEllipseItem):
    def __init__(self, main_window: QMainWindow, x, y, w, h, pen, brush,
                 id_in_list, update_callback):
        super().__init__(x, y, w, h)
        self.setPen(pen)
        self.setBrush(brush)
        # remember main window to change cursor in events
        self._main_window = main_window
        # remember index in list of self (and callback)
        # this is needed to call the update_callback
        self._id_in_list = id_in_list
        self._upd_callback = update_callback

    def mouseMoveEvent(self, event):
        # set position
        self.setPos(event.pos())

    def mousePressEvent(self, event):
        # change cursor
        self._main_window.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))

    def mouseReleaseEvent(self, event):
        # change cursor back
        self._main_window.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        # commit changes
        self._upd_callback(self._id_in_list, event.pos())
