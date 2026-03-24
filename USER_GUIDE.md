# openQCM Dual V2.0 — User Guide

## Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Getting Started](#getting-started)
5. [Interface Overview](#interface-overview)
6. [Connecting to the Device](#connecting-to-the-device)
7. [QCM Frequency Monitoring](#qcm-frequency-monitoring)
8. [Temperature Control & Monitoring](#temperature-control--monitoring)
9. [Data Export (CSV)](#data-export-csv)
10. [Plot Controls](#plot-controls)
11. [Serial Protocol Reference](#serial-protocol-reference)
12. [Troubleshooting](#troubleshooting)

---

## Overview

openQCM Dual V2.0 is a desktop application for real-time monitoring of dual quartz crystal microbalance (QCM) sensors. It communicates with the openQCM Dual hardware (Teensy 4.0 microcontroller) via USB serial, providing:

- Real-time frequency monitoring for two quartz sensors (F1, F2) and their difference (ΔF)
- Moving average filtering with configurable buffer
- TEC (Thermoelectric Cooler) temperature control and monitoring
- Onboard temperature sensor readout
- CSV data export with real-time logging
- Dark-themed, resizable interface

---

## System Requirements

- **Operating System:** Windows 10/11 (64-bit)
- **Hardware:** openQCM Dual board with Teensy 4.0, connected via USB
- **Display:** Minimum 1280×720 resolution recommended

---

## Installation

### Windows Standalone Executable

1. Download `openqcm_double.exe` from the [GitHub Releases](https://github.com/openQCM/openQCM_Dual_Quartz_Sensors/releases) page
2. Place the file in any folder on your computer
3. Double-click to run — no installation required
4. The first launch takes approximately 10 seconds (one-time extraction)

### Running from Source (Python)

1. Install Python 3.8+ and pip
2. Install dependencies:
   ```
   pip install PyQt5 pyqtgraph pyserial numpy
   ```
3. Navigate to the project folder and run:
   ```
   python -m openqcm
   ```

---

## Getting Started

1. Connect the openQCM Dual hardware to your computer via USB
2. Launch the application
3. Select the serial port from the dropdown menu in the sidebar
4. Click **Connect**
5. Frequency data will begin streaming to the charts automatically

---

## Interface Overview

The application window is divided into four main areas:

### Top Bar
Displays the openQCM logo and application title: **openQCM Dual V2.0 — Dual Quartz Sensors**.

### Sidebar (Left Panel)
Contains all controls and live measurement readouts, organized in four sections:

| Section | Description |
|---------|-------------|
| **Serial Connection** | Port selector, Refresh and Connect buttons |
| **Plot Controls** | Autoscale, Clear, and Raw Data toggle buttons |
| **Measurement** | Live frequency readouts (F1, F2, ΔF) |
| **Data** | Save Data button for CSV export |

The sidebar width can be adjusted by dragging the splitter handle between the sidebar and the chart area.

### Chart Area (Center)
Contains two tabs:
- **QCM Monitoring** — Three stacked frequency charts
- **Temperature** — Temperature chart with TEC control

### Status Bar (Bottom)
Displays the current connection status and last received data values.

---

## Connecting to the Device

1. **Select Port:** Use the dropdown to choose the USB serial port corresponding to your openQCM hardware. On Windows this appears as `COMx`.

2. **Refresh:** Click the **Refresh** button to rescan available ports if the device was connected after the application started.

3. **Connect:** Click **Connect** to establish the serial link.
   - The button label changes to **Disconnect** and turns green
   - The status bar shows: `STATUS: Connected to COMx`
   - Data streaming begins automatically

4. **Disconnect:** Click **Disconnect** to close the serial connection.
   - The application stops receiving data but retains all plotted data

**Connection Parameters:**
- Baud rate: 9600 bps
- Data bits: 8, Stop bits: 1, No parity
- Timeout: 1 second

---

## QCM Frequency Monitoring

The **QCM Monitoring** tab displays three synchronized charts stacked vertically:

### Chart 1: Frequency #1 (Hz)
Shows the resonance frequency of the first quartz sensor.

### Chart 2: Frequency #2 (Hz)
Shows the resonance frequency of the second quartz sensor.

### Chart 3: ΔF (Hz)
Shows the difference between the two frequencies: ΔF = F2 − F1.

### Data Traces

Each chart displays two data traces:

| Trace | Appearance | Description |
|-------|------------|-------------|
| **Raw** | Yellow dots (hidden by default) | Individual frequency samples as received |
| **Average** | Blue line | Moving average over the last 10 samples |

The moving average uses a circular buffer of 10 samples. This smooths out noise while maintaining real-time responsiveness.

### Live Measurements

The sidebar **Measurement** section displays the latest averaged values:
- **Frequency #1:** e.g., `10013600.5 Hz`
- **Frequency #2:** e.g., `10020504.2 Hz`
- **Delta Frequency:** e.g., `6903.7 Hz`

These values update with each new sample (every 0.5 seconds at the default gate time).

---

## Temperature Control & Monitoring

Switch to the **Temperature** tab to access temperature features.

### Temperature Chart

The chart displays two traces:

| Trace | Color | Description |
|-------|-------|-------------|
| **TEC** | Red | Temperature measured by the TEC sensor |
| **Onboard** | Green | Temperature from the onboard sensor |

Both traces share the same time axis (seconds).

### Live Temperature Indicators

Below the chart:
- **TEC Temp:** Current TEC sensor reading (e.g., `25.123 °C`)
- **Onboard:** Current onboard sensor reading (e.g., `23.456 °C`)

### Setting the Temperature

1. Enter the desired temperature in the **Set Temperature (°C)** field
   - Range: 5.000 °C to 45.000 °C
   - Precision: 3 decimal places
   - Default: 25.000 °C
2. Click **Set** to send the command to the device
3. The TEC controller on the hardware will regulate to the target temperature

---

## Data Export (CSV)

The application can log all frequency data to a CSV file in real-time.

### Start Logging

1. Click **Save Data** in the sidebar
2. A file dialog opens with a default filename: `openQCM_YYYYMMDD_HHMMSS.csv`
3. Choose the save location and confirm
4. The button changes to **Stop Data** (red border)
5. Status bar shows: `STATUS: Logging to <filename>`

### Stop Logging

1. Click **Stop Data**
2. The CSV file is finalized and closed
3. Status bar briefly shows the number of saved samples

### CSV File Format

The exported CSV file contains the following columns:

```
Date,Time,Relative_Time_s,Frequency_1_Hz,Frequency_2_Hz,Delta_Frequency_Hz
```

| Column | Format | Example |
|--------|--------|---------|
| Date | YYYY-MM-DD | 2026-03-24 |
| Time | HH:MM:SS.mmm | 14:30:45.123 |
| Relative_Time_s | seconds (3 decimals) | 125.500 |
| Frequency_1_Hz | Hz (1 decimal) | 10013600.5 |
| Frequency_2_Hz | Hz (1 decimal) | 10020504.2 |
| Delta_Frequency_Hz | Hz (1 decimal) | 6903.7 |

Data is written in real-time — each sample is flushed to disk immediately. If the application is closed unexpectedly, all data up to that point is preserved.

---

## Plot Controls

### Autoscale
Click **Autoscale** to automatically fit all chart axes to the current data range. This applies to all three QCM charts and the temperature chart simultaneously.

### Clear
Click **Clear** to erase all plotted data and reset the charts to their initial empty state. This also resets the time counter and clears the measurement readouts.

### Raw Data
Click **Raw Data** to toggle the visibility of raw (unfiltered) data points on the QCM charts. When active:
- The button has a yellow border
- Yellow dots appear on all three frequency charts
- The averaged blue line remains visible

This is useful for assessing measurement noise and verifying the effectiveness of the moving average filter.

### Chart Interaction (Right-Click Menu)

Right-click on any chart to access:

| Option | Description |
|--------|-------------|
| **Auto-scale** | Fit both axes to the data |
| **Reset Zoom** | Return to full view |
| **Pan Mode** | Click and drag to pan across the data |
| **Select Mode** | Click and drag to zoom into a selected region |

### Mouse Controls

- **Scroll wheel:** Zoom in/out
- **Click + drag:** Depends on mode (Pan or Select)
- **Right-click:** Open context menu

---

## Serial Protocol Reference

The application communicates with the openQCM Dual hardware using a simple ASCII protocol over USB serial at 9600 baud.

### Incoming Messages (Device → Application)

| Prefix | Format | Description |
|--------|--------|-------------|
| `F` | `F<freq1>,<freq2>,<diff>` | QCM frequency data (three floats) |
| `T` | `T<millidegrees>` | TEC temperature in millidegrees (integer / 1000 = °C) |
| `C` | `C<degrees>` | Onboard temperature in °C (float) |

**Examples:**
```
F10013600,10020504,6904
T25123
C23.5
```

### Outgoing Commands (Application → Device)

| Command | Format | Description |
|---------|--------|-------------|
| Set Temperature | `T<millidegrees>\n` | Set TEC target temperature |

**Example:** To set 25.000 °C, the application sends `T25000\n`.

---

## Troubleshooting

### Device not detected
- Ensure the USB cable is connected and the device is powered on
- Click **Refresh** to rescan for ports
- On Windows, check Device Manager for the correct COM port
- Install the Teensy USB driver if needed

### No data after connecting
- Verify the correct port is selected
- Disconnect and reconnect
- Check that the firmware is running on the Teensy 4.0
- The default baud rate is 9600 — ensure the firmware matches

### Charts not updating
- Check the status bar for error messages
- Click **Clear** and reconnect
- Ensure only one application is using the serial port

### Slow application startup
- The standalone executable (`.exe`) takes ~10 seconds on first launch due to file extraction
- Subsequent launches from the same session are faster
- Running from Python source starts immediately

### CSV file appears empty
- Ensure data is being received before starting the log
- Check the status bar: it should show "Logging to ..."
- The file is written in real-time — check with a text editor while logging

---

*openQCM Dual V2.0 — Developed by openQCM*
*https://openqcm.com*
