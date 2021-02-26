from PySide2.QtWidgets import QApplication, QMainWindow


def entry_point():
    app = QApplication()
    window = QMainWindow()
    window.setWindowTitle("Bezier Splines by S-E-N-S")
    window.show()
    app.exec_()


if __name__ == '__main__':
    entry_point()
