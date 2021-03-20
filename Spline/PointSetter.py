from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton


class PointSetter(QWidget):
    def __init__(self, inc_callback, dec_callback,
                 cur_value, min_value=3, max_value=10):
        super().__init__()
        layout = QVBoxLayout()
        self._label = QLabel("Add/Remove points")
        self._button_holder = QWidget()
        button_holder_layout = QHBoxLayout()
        self._button_minus = QPushButton("-", self)
        self._button_plus = QPushButton("+", self)
        self._inc_callback = inc_callback
        self._dec_callback = dec_callback
        self._min_value = min_value
        self._max_value = max_value
        self._cur_value = cur_value
        self._connect_buttons()
        layout.addWidget(self._label)
        layout.addWidget(self._button_holder)
        button_holder_layout.addWidget(self._button_plus)
        button_holder_layout.addWidget(self._button_minus)
        self._button_holder.setLayout(button_holder_layout)
        self.setLayout(layout)

    def _connect_buttons(self):
        # decorate callbacks
        def button_minus_block():
            # calls each time user clicks "-1" button
            if self._cur_value >= self._min_value:
                # can decrement point count
                self._cur_value -= 1
                self._dec_callback(self._cur_value)
                # disable button if the limit reached
                if self._cur_value <= self._min_value:
                    self._button_minus.setDisabled(True)
                self._button_plus.setEnabled(True)
            else:
                # can't decrement point count
                pass

        def button_plus_block():
            if self._cur_value <= self._max_value:
                # can increment point count
                self._cur_value += 1
                self._inc_callback(self._cur_value)
                # disable button if the limit reached
                if self._cur_value >= self._max_value:
                    self._button_plus.setDisabled(True)
                self._button_minus.setEnabled(True)
            else:
                # can't increment point count
                pass

        self._button_plus.clicked.connect(button_plus_block)
        self._button_minus.clicked.connect(button_minus_block)
