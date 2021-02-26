from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtWidgets import QGraphicsItem, QGraphicsScene, QGraphicsView
from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout


WINDOW_HEIGHT = 600
WINDOW_WIDTH = 800
VIEW_HEIGHT = 300
VIEW_WIDTH = 400


class SplineWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bezier Splines by S-E-N-S")
        self.setFixedWidth(WINDOW_WIDTH)
        self.setFixedHeight(WINDOW_HEIGHT)
        self._create_widgets()

    def _create_widgets(self):
        main_layout = QVBoxLayout(self)

        # create plot area
        scene = QGraphicsScene(self)
        view = QGraphicsView(scene, self)
        view.setFixedHeight(VIEW_HEIGHT)
        view.setFixedWidth(VIEW_WIDTH)
        main_layout.addWidget(view)

        # add everything to the window
        self.setLayout(main_layout)


def entry_point():
    app = QApplication()
    window = SplineWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    entry_point()
