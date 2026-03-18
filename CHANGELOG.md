# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [2.0.0] — 2026-03-17

Complete rewrite from monolithic V1 to modular architecture.

### Added
- **Modular project structure** — separate modules for serial, data model, export, GUI components
- **Resizable sidebar** with sections: Serial Connection, Plot Controls, Measurement, Data
- **Tabbed interface** — QCM Monitoring tab (3 frequency graphs) and Temperature tab
- **Real-time CSV logger** with dedicated writer thread and `queue.Queue` for zero-impact recording
- **Save/Stop toggle** — button changes to "Stop Data" with red styling during active logging
- **Custom right-click context menu** — Auto-scale, Reset Zoom, Pan Mode, Select Mode (replaces pyqtgraph defaults)
- **Raw data scatter dots** (yellow, small) rendered behind averaged line curves (blue)
- **NonScientificAxis** — Y-axis displays plain integers, no scientific notation
- **OneDecimalAxis** — temperature Y-axis with 1 decimal place
- **Top bar branding** — app icon + "openQCM Double V2.0" / "Quartz Crystal Microbalance" aligned right
- **Application icon** support (taskbar + title bar) via `.ico` file
- **PyInstaller one-file build** — `openqcm_double.spec` with `_resource_path()` for bundled assets
- **Entry point** — `python run.py` or `python -m openqcm`
- **Package installer** — `setup.py` with `openqcm-double` console entry point
- **Dark theme** — consistent `#1e1e2e` background with `#89b4fa` accent colors

### Changed
- GUI framework from single-file layout to `QSplitter` + `QTabWidget` architecture
- Window default size from fullscreen to 1100×600 (min 900×500)
- Frequency plots show both raw scatter and moving-average line simultaneously
- Status bar shows only filename (not full path) during logging
- Stop logging resets status bar to "Connected" instead of showing saved count

### Fixed
- **Autoscale persistence** — removed `autoRange()` call that internally disabled continuous auto-range
- **Scientific notation on Y-axis** — custom `AxisItem` subclass with `enableAutoSIPrefix(False)` applied after axis attachment

---

## [1.0.0] — 2026-03-01

Initial release — monolithic single-file Python application.

### Features
- Serial connection to Teensy 4.0 via USB
- Real-time frequency plotting (Frequency #1, #2, Delta)
- Temperature monitoring (TEC + onboard)
- Basic pyqtgraph interface with default styling
