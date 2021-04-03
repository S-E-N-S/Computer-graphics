from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PySide2.QtGui import QCursor
from PySide2.QtCore import Qt  # for cursor shapes


class PointSetter(QWidget):
    def __init__(self, inc_callback, dec_callback,
                 cur_value, min_value=3, max_value=10):
        super().__init__()
        layout = QVBoxLayout()
        self._label = QLabel("Add/Remove points")
        self._button_holder = QWidget()
        button_holder_layout = QHBoxLayout()
        self.button_minus = QPushButton("-", self)
        self.button_plus = QPushButton("+", self)
        self._inc_callback = inc_callback
        self._dec_callback = dec_callback
        self._min_value = min_value
        self._max_value = max_value
        self._cur_value = cur_value
        self._connect_buttons()
        layout.addWidget(self._label)
        layout.addWidget(self._button_holder)
        button_holder_layout.addWidget(self.button_plus)
        button_holder_layout.addWidget(self.button_minus)
        self._button_holder.setLayout(button_holder_layout)
        self.setLayout(layout)
        self.active = True

    def can_unblock_plus(self):
        return self._cur_value < self._max_value

    def _connect_buttons(self):
        # decorate callbacks
        def button_minus_block():
            # calls each time user clicks "-1" button
            if self._cur_value >= self._min_value:
                # can decrement point count
                self._cur_value -= 1
                self._dec_callback()
                # disable button if the limit reached
                if self._cur_value <= self._min_value:
                    self.button_minus.setDisabled(True)
                self.button_plus.setEnabled(True)
            else:
                # can't decrement point count
                pass

        def button_plus_block():
            if self._cur_value <= self._max_value:
                # can increment point count
                self._cur_value += 1
                self._inc_callback()
                # disable button if the limit reached
                self.button_plus.setDisabled(True)
                self.button_minus.setDisabled(True)
            else:
                # can't increment point count
                pass

        self.button_plus.clicked.connect(button_plus_block)
        self.button_minus.clicked.connect(button_minus_block)
