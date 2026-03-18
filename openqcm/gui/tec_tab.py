"""Temperature tab — TEC and onboard temperature monitoring + setpoint control."""

import pyqtgraph as pg
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QDoubleSpinBox,
)
from PyQt5.QtCore import pyqtSignal

from ..config import TEC_TEMP_MIN, TEC_TEMP_MAX, TEC_TEMP_DEFAULT, TEC_TEMP_DECIMALS
from .style import PEN_TEMP, PEN_ONBOARD, configure_plot_widget


class TECTab(QWidget):
    """Tab for TEC + onboard temperature monitoring and setpoint control."""

    set_temperature = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tec_data = []
        self._onboard_data = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Temperature graph
        self.graph = pg.PlotWidget()
        configure_plot_widget(self.graph, left_label="°C", axis_type="decimal")
        self.tec_curve = self.graph.plot(pen=PEN_TEMP, name="TEC")
        self.onboard_curve = self.graph.plot(pen=PEN_ONBOARD, name="Onboard")
        self.graph.addLegend(offset=(10, 10))
        layout.addWidget(self.graph, stretch=3)

        # Indicators row
        info = QHBoxLayout()
        info.setSpacing(24)
        self.tec_temp_label = self._make_indicator("TEC Temp:", info)
        self.onboard_temp_label = self._make_indicator("Onboard:", info)
        info.addStretch()
        layout.addLayout(info)

        # TEC setpoint controls
        ctrl = QHBoxLayout()
        ctrl.setSpacing(8)

        lbl = QLabel("Set Temperature (°C):")
        lbl.setObjectName("section_label")
        ctrl.addWidget(lbl)

        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(TEC_TEMP_MIN, TEC_TEMP_MAX)
        self.temp_spin.setDecimals(TEC_TEMP_DECIMALS)
        self.temp_spin.setValue(TEC_TEMP_DEFAULT)
        ctrl.addWidget(self.temp_spin)

        self.set_btn = QPushButton("Set")
        self.set_btn.clicked.connect(self._on_set)
        ctrl.addWidget(self.set_btn)

        ctrl.addStretch()
        layout.addLayout(ctrl)

    @staticmethod
    def _make_indicator(title, parent_layout):
        lbl_title = QLabel(title)
        lbl_title.setObjectName("section_label")
        parent_layout.addWidget(lbl_title)
        lbl_value = QLabel("—")
        lbl_value.setObjectName("value_label")
        lbl_value.setMinimumWidth(80)
        parent_layout.addWidget(lbl_value)
        return lbl_value

    def _on_set(self):
        self.set_temperature.emit(self.temp_spin.value())

    def update_temperature(self, temp):
        self._tec_data.append(temp)
        self.tec_curve.setData(self._tec_data)
        self.tec_temp_label.setText(f"{temp:.3f} °C")

    def update_onboard_temperature(self, temp):
        self._onboard_data.append(temp)
        self.onboard_curve.setData(self._onboard_data)
        self.onboard_temp_label.setText(f"{temp:.3f} °C")

    def set_xlink(self, source_graph):
        self.graph.setXLink(source_graph)

    def autoscale(self):
        self.graph.enableAutoRange(axis='y')

    def clear(self):
        self._tec_data.clear()
        self._onboard_data.clear()
        self.tec_curve.setData([], [])
        self.onboard_curve.setData([], [])
        self.tec_temp_label.setText("—")
        self.onboard_temp_label.setText("—")
