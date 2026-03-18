"""QCM monitoring tab — three frequency graphs with raw + averaged curves."""

import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from .style import PEN_RAW, PEN_AVG, SYMBOL_RAW, configure_plot_widget


class QCMTab(QWidget):
    """Tab displaying Frequency #1, Frequency #2, and their difference."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        self.graphs = []
        self.avg_curves = []
        self.raw_curves = []

        labels = ["Frequency #1  (Hz)", "Frequency #2  (Hz)", "ΔF  (Hz)"]

        self._raw_visible = False

        for i, label in enumerate(labels):
            pw = pg.PlotWidget()
            configure_plot_widget(pw, left_label=label)
            if i > 0:
                pw.setXLink(self.graphs[0])

            # Raw added first → drawn behind; avg added second → drawn on top
            raw_curve = pw.plot(pen=PEN_RAW, name="Raw", **SYMBOL_RAW)
            raw_curve.setZValue(-1)
            raw_curve.setVisible(False)

            avg_curve = pw.plot(pen=PEN_AVG, name="Avg")
            avg_curve.setZValue(1)

            layout.addWidget(pw, stretch=1)

            self.graphs.append(pw)
            self.avg_curves.append(avg_curve)
            self.raw_curves.append(raw_curve)

    def set_raw_visible(self, visible):
        """Show or hide raw scatter dots on all graphs."""
        self._raw_visible = visible
        for curve in self.raw_curves:
            curve.setVisible(visible)

    def update_plots(self, time, raw, avg):
        keys = ["freq1", "freq2", "diff"]
        for i, key in enumerate(keys):
            self.avg_curves[i].setData(time, avg[key])
            if self._raw_visible:
                self.raw_curves[i].setData(time, raw[key])

    def autoscale(self):
        self.graphs[0].enableAutoRange(axis='x')
        for pw in self.graphs:
            pw.enableAutoRange(axis='y')

    def clear(self):
        for i in range(3):
            self.avg_curves[i].setData([], [])
            self.raw_curves[i].setData([], [])
