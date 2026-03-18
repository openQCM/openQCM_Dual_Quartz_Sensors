"""Application constants and configuration."""

# Serial
BAUDRATE = 9600
SERIAL_TIMEOUT = 1

# QCM acquisition
GATE_TIME = 0.5       # seconds between samples
BUFFER_SIZE = 10      # circular buffer length for moving average

# TEC temperature limits
TEC_TEMP_MIN = 5.0    # °C
TEC_TEMP_MAX = 45.0   # °C
TEC_TEMP_DEFAULT = 25.0
TEC_TEMP_DECIMALS = 3
