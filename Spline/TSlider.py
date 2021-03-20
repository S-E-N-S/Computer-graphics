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

    def set_value(self, new_value):
        self._sld.setValue(new_value)

    def _init_slider(self, update_callback, layout, value):
        self._sld = QSlider(Qt.Horizontal, self)
        self._sld.setFocusPolicy(Qt.NoFocus)
        self._sld.setValue(value)
        self._sld.setGeometry(30, 40, 100, 30)
        self._sld.valueChanged[int].connect(update_callback)
        layout.addWidget(self._sld)
    
    def _init_label(self, layout):
        self.label = QLabel(self)
        layout.addWidget(self.label)
