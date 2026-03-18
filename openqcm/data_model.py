"""QCM data model with circular-buffer averaging."""

from datetime import datetime

from .config import BUFFER_SIZE, GATE_TIME


class QCMData:
    """Stores raw and averaged frequency data for both channels."""

    def __init__(self, buffer_size=BUFFER_SIZE, gate_time=GATE_TIME):
        self.buffer_size = buffer_size
        self.gate_time = gate_time
        self.reset()

    def reset(self):
        """Clear all data and reinitialise buffers."""
        self.time = []
        self.timestamps = []  # absolute datetime for each sample
        self.raw = {"freq1": [], "freq2": [], "diff": []}
        self.avg = {"freq1": [], "freq2": [], "diff": []}

        self._buffer = {
            "freq1": [0.0] * self.buffer_size,
            "freq2": [0.0] * self.buffer_size,
            "diff": [0.0] * self.buffer_size,
        }
        self._buf_idx = 0
        self._counter = 0
        self._initialised = False

    def add_sample(self, freq1, freq2, diff):
        """Add a new sample, update buffers, return averaged values."""
        if not self._initialised:
            for key, val in [("freq1", freq1), ("freq2", freq2), ("diff", diff)]:
                self._buffer[key] = [val] * self.buffer_size
            self._initialised = True
            self._buf_idx = 0
        else:
            self._buffer["freq1"][self._buf_idx] = freq1
            self._buffer["freq2"][self._buf_idx] = freq2
            self._buffer["diff"][self._buf_idx] = diff
            self._buf_idx = (self._buf_idx + 1) % self.buffer_size

        # Timestamp
        self.timestamps.append(datetime.now())

        # Raw data
        self.raw["freq1"].append(freq1)
        self.raw["freq2"].append(freq2)
        self.raw["diff"].append(diff)

        # Averaged data
        avg1 = sum(self._buffer["freq1"]) / self.buffer_size
        avg2 = sum(self._buffer["freq2"]) / self.buffer_size
        avg_d = sum(self._buffer["diff"]) / self.buffer_size
        self.avg["freq1"].append(avg1)
        self.avg["freq2"].append(avg2)
        self.avg["diff"].append(avg_d)

        # Time axis
        t = self._counter * self.gate_time
        self.time.append(t)
        self._counter += 1

        return freq1, freq2, diff, avg1, avg2, avg_d
