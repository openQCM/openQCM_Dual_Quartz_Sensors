"""Main application window — sidebar, tabs, and status bar."""

import os
import sys
from datetime import datetime

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QMessageBox, QSplitter, QFileDialog,
)
from PyQt5.QtCore import Qt

from .. import __version__
from ..serial_comm import SerialCommunicator


_ICON_DIR = os.path.join(os.path.dirname(__file__), "assets")
if hasattr(sys, "_MEIPASS"):
    _ICON_DIR = os.path.join(sys._MEIPASS, "openqcm", "gui", "assets")
_ICON_PATH = os.path.join(_ICON_DIR, "openqcm.ico")
from ..data_model import QCMData
from ..data_export import CSVLogger
from .sidebar import Sidebar
from .qcm_tab import QCMTab
from .tec_tab import TECTab


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"openQCM Dual  v{__version__}")
        self.setMinimumSize(900, 650)
        self.resize(1100, 600)

        self._serial = None
        self._qcm = QCMData()
        self._csv_logger = CSVLogger()

        self._build_ui()

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # --- Top bar: branding right-aligned ---
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(12, 8, 12, 4)
        top_bar.setSpacing(8)
        top_bar.addStretch()

        if os.path.exists(_ICON_PATH):
            icon_label = QLabel()
            pixmap = QPixmap(_ICON_PATH).scaled(
                28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation,
            )
            icon_label.setPixmap(pixmap)
            top_bar.addWidget(icon_label)

        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        app_title = QLabel("openQCM Dual V2.0")
        app_title.setObjectName("brand_title")
        title_layout.addWidget(app_title)
        app_subtitle = QLabel("Dual Quartz Sensors")
        app_subtitle.setObjectName("brand_subtitle")
        title_layout.addWidget(app_subtitle)
        top_bar.addLayout(title_layout)

        outer.addLayout(top_bar)

        # --- Main area: resizable sidebar + tabs ---
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(True)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.connect_requested.connect(self._connect)
        self.sidebar.disconnect_requested.connect(self._disconnect)
        self.sidebar.autoscale_requested.connect(self._autoscale)
        self.sidebar.clear_requested.connect(self._clear)
        self.sidebar.save_requested.connect(self._start_logging)
        self.sidebar.stop_save_requested.connect(self._stop_logging)
        self.sidebar.setMinimumWidth(60)
        self.sidebar.setMaximumWidth(350)
        splitter.addWidget(self.sidebar)

        # Tabs
        self.tabs = QTabWidget()
        self.qcm_tab = QCMTab()
        self.tec_tab = TECTab()
        self.tabs.addTab(self.qcm_tab, "QCM Monitoring")
        self.tabs.addTab(self.tec_tab, "Temperature")
        splitter.addWidget(self.tabs)

        self.sidebar.raw_toggled.connect(self.qcm_tab.set_raw_visible)

        # Sidebar starts at 220px, tabs get the rest
        splitter.setSizes([220, 780])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        outer.addWidget(splitter, stretch=1)

        # Link TEC x-axis to first QCM graph
        if self.qcm_tab.graphs:
            self.tec_tab.set_xlink(self.qcm_tab.graphs[0])

        # TEC setpoint
        self.tec_tab.set_temperature.connect(self._send_temperature)

        # --- Bottom status bar ---
        status_bar = QHBoxLayout()
        status_bar.setContentsMargins(12, 6, 12, 6)
        status_bar.setSpacing(12)

        self.status_label = QLabel("STATUS: Disconnected")
        self.status_label.setObjectName("status_label")
        status_bar.addWidget(self.status_label)

        status_bar.addStretch()

        self.last_data_label = QLabel("")
        self.last_data_label.setObjectName("status_label")
        status_bar.addWidget(self.last_data_label)

        status_widget = QWidget()
        status_widget.setObjectName("status_bar")
        status_widget.setLayout(status_bar)
        outer.addWidget(status_widget)

    # --- Serial lifecycle ---

    def _connect(self, port):
        try:
            self._serial = SerialCommunicator(port)
            self._serial.data_received.connect(self._on_data)
            self._serial.error_occurred.connect(self._on_error)
            self.sidebar.set_connected(True)
            self._set_status(f"Connected to {port}")
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", str(e))

    def _disconnect(self):
        if self._serial:
            self._serial.stop()
            self._serial = None
        self.sidebar.set_connected(False)
        self._set_status("Disconnected")

    def _set_status(self, text):
        self.status_label.setText(f"STATUS: {text}")

    # --- Data handling ---

    def _on_data(self, data):
        if data.startswith("F"):
            self._handle_qcm(data)
        elif data.startswith("T"):
            self._handle_tec_temp(data)
        elif data.startswith("C"):
            self._handle_onboard_temp(data)

    def _handle_qcm(self, data):
        try:
            parts = data.split(",")
            if len(parts) != 3:
                return
            freq1 = float(parts[0][1:])
            freq2 = float(parts[1])
            diff = float(parts[2])
            _r1, _r2, _rd, a1, a2, ad = self._qcm.add_sample(freq1, freq2, diff)
            self.qcm_tab.update_plots(
                self._qcm.time, self._qcm.raw, self._qcm.avg,
            )
            self.sidebar.update_measurements(a1, a2, ad)
            self.last_data_label.setText(
                f"F1: {a1:.1f}  F2: {a2:.1f}  ΔF: {ad:.1f} Hz"
            )

            # Real-time CSV logging (non-blocking queue put)
            if self._csv_logger.is_open:
                self._csv_logger.enqueue(
                    self._qcm.timestamps[-1],
                    self._qcm.time[-1],
                    a1, a2, ad,
                )
        except ValueError:
            pass

    def _handle_tec_temp(self, data):
        try:
            temp = int(data[1:]) / 1000.0
            self.tec_tab.update_temperature(temp)
        except ValueError:
            pass

    def _handle_onboard_temp(self, data):
        try:
            temp = float(data[1:])
            self.tec_tab.update_onboard_temperature(temp)
        except ValueError:
            pass

    # --- Commands ---

    def _send_temperature(self, temp_c):
        if self._serial:
            self._serial.write(f"T{int(temp_c * 1000)}")

    def _clear(self):
        self._qcm.reset()
        self.qcm_tab.clear()
        self.tec_tab.clear()
        self.last_data_label.setText("")

    def _autoscale(self):
        self.qcm_tab.autoscale()
        self.tec_tab.autoscale()

    # --- Data logging (real-time CSV) ---

    def _start_logging(self):
        default_name = f"openQCM_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Data", default_name,
            "CSV Files (*.csv);;All Files (*)",
        )
        if not filepath:
            return

        try:
            self._csv_logger.open(filepath)
            self.sidebar.set_logging(True)
            self._set_status(f"Logging to {os.path.basename(filepath)}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    def _stop_logging(self):
        if not self._csv_logger.is_open:
            return

        filepath, count = self._csv_logger.close()
        self.sidebar.set_logging(False)
        self._set_status("Connected")
        self.last_data_label.setText("")

    # --- Cleanup ---

    def _on_error(self, error):
        QMessageBox.critical(self, "Serial Error", error)
        self._disconnect()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "Quit",
            "Are you sure you want to close the application?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply == QMessageBox.No:
            event.ignore()
            return

        if self._csv_logger.is_open:
            self._csv_logger.close()
        self._disconnect()
        event.accept()
