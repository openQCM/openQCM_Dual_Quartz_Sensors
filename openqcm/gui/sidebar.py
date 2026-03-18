"""Left sidebar — serial connection, plot controls, live measurements."""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QFrame,
)
from PyQt5.QtCore import pyqtSignal, Qt

from ..serial_comm import list_serial_ports


class Sidebar(QWidget):
    """Sidebar with serial connection, plot controls, and measurement readouts."""

    connect_requested = pyqtSignal(str)
    disconnect_requested = pyqtSignal()
    autoscale_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    save_requested = pyqtSignal()
    stop_save_requested = pyqtSignal()
    raw_toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self._connected = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        # --- Serial Connection ---
        layout.addWidget(self._section_label("Serial Connection"))

        self.port_combo = QComboBox()
        layout.addWidget(self.port_combo)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(4)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        btn_row.addWidget(self.refresh_btn)

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setObjectName("connect_btn")
        self.connect_btn.clicked.connect(self._toggle)
        btn_row.addWidget(self.connect_btn)

        layout.addLayout(btn_row)

        layout.addWidget(self._separator())

        # --- Plot Controls ---
        layout.addWidget(self._section_label("Plot Controls"))

        self.autoscale_btn = QPushButton("Autoscale")
        self.autoscale_btn.clicked.connect(self.autoscale_requested.emit)
        layout.addWidget(self.autoscale_btn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_requested.emit)
        layout.addWidget(self.clear_btn)

        self._raw_visible = False
        self.raw_btn = QPushButton("Raw Data")
        self.raw_btn.setObjectName("raw_btn")
        self.raw_btn.setCheckable(True)
        self.raw_btn.setChecked(False)
        self.raw_btn.clicked.connect(self._toggle_raw)
        layout.addWidget(self.raw_btn)

        layout.addWidget(self._separator())

        # --- Measurement ---
        layout.addWidget(self._section_label("Measurement"))

        self.freq1_label = self._value_row("Frequency #1", layout)
        self.freq2_label = self._value_row("Frequency #2", layout)
        self.diff_label = self._value_row("Delta Frequency", layout)

        layout.addWidget(self._separator())

        # --- Data ---
        layout.addWidget(self._section_label("Data"))

        self._logging = False
        self.save_btn = QPushButton("Save Data")
        self.save_btn.setObjectName("save_btn")
        self.save_btn.clicked.connect(self._toggle_save)
        layout.addWidget(self.save_btn)

        layout.addStretch()

        self.refresh_ports()

    # --- Public API ---

    def refresh_ports(self):
        self.port_combo.clear()
        for port in list_serial_ports():
            self.port_combo.addItem(port)

    def set_connected(self, connected):
        self._connected = connected
        self.connect_btn.setText("Disconnect" if connected else "Connect")
        self.connect_btn.setProperty("connected", str(connected).lower())
        self.connect_btn.style().unpolish(self.connect_btn)
        self.connect_btn.style().polish(self.connect_btn)
        self.port_combo.setEnabled(not connected)
        self.refresh_btn.setEnabled(not connected)

    def set_logging(self, active):
        self._logging = active
        if active:
            self.save_btn.setText("Stop Data")
            self.save_btn.setProperty("logging", "true")
        else:
            self.save_btn.setText("Save Data")
            self.save_btn.setProperty("logging", "false")
        self.save_btn.style().unpolish(self.save_btn)
        self.save_btn.style().polish(self.save_btn)

    def update_measurements(self, freq1, freq2, diff):
        self.freq1_label.setText(f"{freq1:.1f} Hz")
        self.freq2_label.setText(f"{freq2:.1f} Hz")
        self.diff_label.setText(f"{diff:.1f} Hz")

    # --- Helpers ---

    def _toggle_raw(self):
        self._raw_visible = self.raw_btn.isChecked()
        self.raw_toggled.emit(self._raw_visible)

    def _toggle_save(self):
        if self._logging:
            self.stop_save_requested.emit()
        else:
            self.save_requested.emit()

    def _toggle(self):
        if self._connected:
            self.disconnect_requested.emit()
        else:
            port = self.port_combo.currentText()
            if port:
                self.connect_requested.emit(port)

    @staticmethod
    def _section_label(text):
        lbl = QLabel(text)
        lbl.setObjectName("section_label")
        return lbl

    @staticmethod
    def _separator():
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("separator")
        return line

    @staticmethod
    def _value_row(title, parent_layout):
        title_lbl = QLabel(title)
        title_lbl.setObjectName("measurement_title")
        parent_layout.addWidget(title_lbl)

        value_lbl = QLabel("—")
        value_lbl.setObjectName("measurement_value")
        parent_layout.addWidget(value_lbl)
        return value_lbl
