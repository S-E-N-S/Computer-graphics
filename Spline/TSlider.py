from PySide2.QtWidgets import QSlider, QWidget, QLabel, QVBoxLayout
from PySide2.QtCore import Qt  # for cursor shapes


class TSlider(QWidget):
    def __init__(self, update_callback, value):
        super().__init__()
        layout = QVBoxLayout(self)
        self._init_label(layout)
        self._init_slider(update_callback, layout, value)
        self.setLayout(layout)

    def add_text(self, t):
        self.label.setText(f't = {t}')

    def _init_slider(self, update_callback, layout, value):
        sld = QSlider(Qt.Horizontal, self)
        sld.setFocusPolicy(Qt.NoFocus)
        sld.setValue(value)
        sld.setGeometry(30, 40, 100, 30)
        sld.valueChanged[int].connect(update_callback)
        layout.addWidget(sld)
    
    def _init_label(self, layout):
        self.label = QLabel(self)
        layout.addWidget(self.label)
