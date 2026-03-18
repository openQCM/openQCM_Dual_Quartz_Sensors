# openQCM Dual V2.0

**Real-time GUI software for the openQCM Dual Quartz Sensors**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
[![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![Teensy 4.0](https://img.shields.io/badge/Firmware-Teensy%204.0-orange.svg)](https://www.pjrc.com/store/teensy40.html)

Real-time frequency acquisition, visualization and data logging for the [openQCM Dual](https://openqcm.com/) system with Teensy 4.0 firmware.

---

## Features

- **Dual oscillator monitoring** — simultaneous acquisition of two independent quartz crystal frequencies and their difference
- **Real-time plotting** — raw scatter data and moving-average curves with interactive zoom, pan and autoscale
- **Temperature control** — TEC setpoint and onboard temperature monitoring
- **CSV data logging** — dedicated writer thread with queue for zero-impact, zero-loss real-time recording
- **Dark theme GUI** — modern interface with resizable sidebar, tabbed views and bottom status bar
- **Cross-platform** — runs on macOS, Windows and Linux

## Requirements

- Python 3.8+
- Teensy 4.0 with openQCM Dual firmware connected via USB

## Installation

```bash
git clone https://github.com/openQCM/openQCM_Dual_Quartz_Sensors.git
cd openQCM_Dual_Quartz_Sensors
pip install -r requirements.txt
```

## Usage

```bash
python run.py
```

Or as a module:

```bash
python -m openqcm
```

## Project Structure

```
openQCM_Dual_Quartz_Sensors/
├── run.py                  # Entry point
├── requirements.txt        # Python dependencies
├── setup.py                # Package installer
├── openqcm_double.spec     # PyInstaller one-file build spec
├── openqcm/
│   ├── __init__.py         # Version
│   ├── __main__.py         # App launcher
│   ├── config.py           # Constants (baudrate, gate time, buffer)
│   ├── serial_comm.py      # USB-serial communication with Teensy
│   ├── data_model.py       # Circular buffer and averaging
│   ├── data_export.py      # Thread-based CSV logger
│   └── gui/
│       ├── main_window.py  # Main window layout
│       ├── sidebar.py      # Left sidebar controls
│       ├── qcm_tab.py      # Frequency plots (3 graphs)
│       ├── tec_tab.py      # Temperature plots
│       ├── style.py        # Theme, custom axes, context menu
│       └── assets/
│           └── openqcm.ico # Application icon
```

## Serial Protocol

The firmware sends ASCII lines over USB-serial at 9600 baud:

| Prefix | Format | Description |
|--------|--------|-------------|
| `F` | `F<freq1>,<freq2>,<diff>` | Frequency data (Hz) |
| `T` | `T<millidegrees>` | TEC temperature |
| `C` | `C<degrees>` | Onboard temperature |

## Building Executable

Single-file executable via PyInstaller:

```bash
pip install pyinstaller
pyinstaller openqcm_double.spec
```

Output: `dist/openQCM_Dual`

## License

MIT — see [LICENSE](LICENSE).
