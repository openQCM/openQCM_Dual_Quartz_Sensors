"""Serial communication handler for openQCM Dual."""

import threading

import serial
import serial.tools.list_ports
from PyQt5.QtCore import QObject, pyqtSignal

from .config import BAUDRATE, SERIAL_TIMEOUT


def list_serial_ports():
    """Return list of available serial port device names."""
    return [p.device for p in serial.tools.list_ports.comports()]


class SerialCommunicator(QObject):
    """Threaded serial reader that emits Qt signals on data/error."""

    data_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, port_name, baudrate=BAUDRATE):
        super().__init__()
        self.ser = serial.Serial(port_name, baudrate=baudrate, timeout=SERIAL_TIMEOUT)
        self.running = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def _read_loop(self):
        while self.running:
            try:
                if self.ser.in_waiting > 0:
                    data = self.ser.readline().decode("utf-8", errors="ignore").strip()
                    if data:
                        self.data_received.emit(data)
            except Exception as e:
                self.error_occurred.emit(str(e))
                break

    def write(self, data):
        """Send a string (with newline) to the device."""
        self.ser.write((data + "\n").encode())

    def stop(self):
        """Stop the reader thread and close the port."""
        self.running = False
        if self.ser.is_open:
            self.ser.close()
        self._thread.join(timeout=2)
