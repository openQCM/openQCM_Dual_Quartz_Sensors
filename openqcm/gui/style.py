"""Minimal dark theme stylesheet for openQCM Dual."""

import pyqtgraph as pg

# Colours
BG = "#1e1e2e"
SURFACE = "#282838"
BORDER = "#3a3a4a"
TEXT = "#cdd6f4"
TEXT_DIM = "#7f849c"
ACCENT = "#89b4fa"
ACCENT_HOVER = "#74c7ec"
RED = "#f38ba8"
GREEN = "#a6e3a1"
YELLOW = "#f9e2af"

# Plot pens / symbols
PEN_RAW = None  # no line for raw — dots only
SYMBOL_RAW = {"symbol": "o", "symbolSize": 1, "symbolBrush": YELLOW, "symbolPen": None}
PEN_AVG = pg.mkPen(color=ACCENT, width=2)
PEN_TEMP = pg.mkPen(color=RED, width=2)
PEN_ONBOARD = pg.mkPen(color=GREEN, width=1.5)

STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {BG};
    color: {TEXT};
    font-family: "SF Pro Text", "Segoe UI", "Roboto", sans-serif;
    font-size: 13px;
}}

/* --- Sidebar --- */
QWidget#sidebar {{
    background-color: {SURFACE};
    border-right: 1px solid {BORDER};
}}

/* --- Status bar --- */
QWidget#status_bar {{
    background-color: {SURFACE};
    border-top: 1px solid {BORDER};
}}

/* --- Tabs --- */
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 6px;
    background: {SURFACE};
    margin-top: -1px;
}}
QTabBar::tab {{
    background: {BG};
    color: {TEXT_DIM};
    padding: 8px 20px;
    border: 1px solid transparent;
    border-bottom: 2px solid transparent;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    color: {TEXT};
    border-bottom: 2px solid {ACCENT};
}}
QTabBar::tab:hover {{
    color: {TEXT};
}}

/* --- Buttons --- */
QPushButton {{
    background-color: {SURFACE};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 6px 12px;
    min-height: 24px;
}}
QPushButton:hover {{
    background-color: {BORDER};
    border-color: {ACCENT};
}}
QPushButton:pressed {{
    background-color: {ACCENT};
    color: {BG};
}}
QPushButton#connect_btn[connected="true"] {{
    border-color: {GREEN};
    color: {GREEN};
}}
QPushButton#save_btn[logging="true"] {{
    border-color: {RED};
    color: {RED};
}}
QPushButton#raw_btn:checked {{
    border-color: {YELLOW};
    color: {YELLOW};
}}

/* --- Inputs --- */
QComboBox {{
    background-color: {BG};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 5px 10px;
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox QAbstractItemView {{
    background-color: {SURFACE};
    color: {TEXT};
    selection-background-color: {ACCENT};
    selection-color: {BG};
    border: 1px solid {BORDER};
}}
QDoubleSpinBox {{
    background-color: {BG};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 5px 8px;
}}

/* --- Labels --- */
QLabel {{
    color: {TEXT};
    padding: 2px;
}}
QLabel#section_label {{
    color: {TEXT_DIM};
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    padding: 8px 0 2px 0;
}}
QLabel#measurement_title {{
    color: {TEXT_DIM};
    font-size: 11px;
    padding: 4px 0 0 0;
}}
QLabel#measurement_value {{
    color: {ACCENT};
    font-size: 16px;
    font-weight: 600;
    padding: 0 0 4px 0;
}}
QLabel#value_label {{
    color: {TEXT};
    font-size: 14px;
    font-weight: 500;
}}
QLabel#status_label {{
    color: {TEXT_DIM};
    font-size: 12px;
}}

/* --- Splitter handle --- */
QSplitter::handle:horizontal {{
    background-color: {BORDER};
    width: 3px;
}}
QSplitter::handle:horizontal:hover {{
    background-color: {ACCENT};
}}

/* --- Separator --- */
QFrame#separator {{
    color: {BORDER};
    margin: 6px 0;
}}

/* --- App branding (status bar) --- */
QLabel#brand_title {{
    color: {TEXT};
    font-size: 13px;
    font-weight: 700;
    padding: 0;
}}
QLabel#brand_subtitle {{
    color: {TEXT_DIM};
    font-size: 10px;
    font-weight: 400;
    padding: 0;
}}
"""


# ---------------------------------------------------------------------------
# Custom axis classes
# ---------------------------------------------------------------------------

class NonScientificAxis(pg.AxisItem):
    """Axis that displays values as plain integers — no scientific notation."""

    def tickStrings(self, values, scale, spacing):
        return [f"{int(v)}" for v in values]


class OneDecimalAxis(pg.AxisItem):
    """Axis that displays values with exactly 1 decimal place."""

    def tickStrings(self, values, scale, spacing):
        return [f"{v:.1f}" for v in values]


# ---------------------------------------------------------------------------
# Plot configuration helpers
# ---------------------------------------------------------------------------

def configure_plot_widget(pw, left_label="", bottom_label="Time (s)",
                          axis_type="integer"):
    """Apply minimal styling to a pyqtgraph PlotWidget.

    axis_type: "integer" for NonScientificAxis, "decimal" for OneDecimalAxis
    """
    # Replace left axis with custom axis
    if axis_type == "decimal":
        custom_axis = OneDecimalAxis(orientation="left")
    else:
        custom_axis = NonScientificAxis(orientation="left")
    pw.setAxisItems({"left": custom_axis})

    # Disable SI prefix AFTER axis is attached
    pw.getAxis("left").enableAutoSIPrefix(False)

    pw.setBackground(SURFACE)
    pw.getAxis("left").setPen(pg.mkPen(color=TEXT_DIM))
    pw.getAxis("bottom").setPen(pg.mkPen(color=TEXT_DIM))
    pw.getAxis("left").setTextPen(pg.mkPen(color=TEXT_DIM))
    pw.getAxis("bottom").setTextPen(pg.mkPen(color=TEXT_DIM))
    pw.setLabel("left", left_label, color=TEXT_DIM)
    pw.setLabel("bottom", bottom_label, color=TEXT_DIM)
    pw.showGrid(x=True, y=True, alpha=0.15)

    # Disable default context menu and install custom one
    _install_context_menu(pw)


def _install_context_menu(pw):
    """Replace pyqtgraph's default right-click menu with a custom one."""
    from PyQt5 import QtCore, QtWidgets

    plot_item = pw.getPlotItem()
    plot_item.setMenuEnabled(False)
    plot_item.getViewBox().setMenuEnabled(False)

    def on_right_click(event):
        if event.button() != QtCore.Qt.RightButton:
            return

        menu = QtWidgets.QMenu()
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {SURFACE};
                color: {TEXT};
                border: 1px solid {BORDER};
                padding: 4px;
            }}
            QMenu::item:selected {{
                background-color: {ACCENT};
                color: {BG};
            }}
            QMenu::separator {{
                height: 1px;
                background: {BORDER};
                margin: 4px 8px;
            }}
        """)

        act_autoscale = menu.addAction("Auto-scale")
        act_reset = menu.addAction("Reset Zoom")
        menu.addSeparator()
        act_pan = menu.addAction("Pan Mode")
        act_select = menu.addAction("Select Mode")

        pos = event.screenPos()
        action = menu.exec_(QtCore.QPoint(int(pos.x()), int(pos.y())))

        if action == act_autoscale:
            pw.enableAutoRange()
        elif action == act_reset:
            pw.getViewBox().autoRange()
        elif action == act_pan:
            pw.getViewBox().setMouseMode(pg.ViewBox.PanMode)
        elif action == act_select:
            pw.getViewBox().setMouseMode(pg.ViewBox.RectMode)

        event.accept()

    plot_item.scene().sigMouseClicked.connect(on_right_click)
