"""Real-time CSV data logger with dedicated writer thread.

Architecture:
- GUI thread calls enqueue() — puts data into a queue.Queue (~nanoseconds, non-blocking)
- A dedicated daemon thread reads from the queue and writes to disk with immediate flush
- Zero impact on GUI responsiveness, zero data loss (every row flushed immediately)
"""

import csv
import threading
import queue
from datetime import datetime

HEADER = [
    "Date", "Time", "Relative_Time_s",
    "Frequency_1_Hz", "Frequency_2_Hz", "Delta_Frequency_Hz",
]

_SENTINEL = object()  # signals the writer thread to stop


class CSVLogger:
    """Thread-safe, queue-based CSV logger: open → enqueue (per sample) → close."""

    def __init__(self):
        self._queue = None
        self._thread = None
        self._filepath = None
        self._row_count = 0
        self._lock = threading.Lock()

    @property
    def is_open(self):
        return self._thread is not None and self._thread.is_alive()

    @property
    def filepath(self):
        return self._filepath

    @property
    def row_count(self):
        return self._row_count

    def open(self, filepath):
        """Start the writer thread and open *filepath* for writing."""
        if self.is_open:
            raise RuntimeError("Logger already open")

        self._filepath = filepath
        self._row_count = 0
        self._queue = queue.Queue()

        self._thread = threading.Thread(
            target=self._writer_loop,
            args=(filepath, self._queue),
            daemon=True,
            name="csv-writer",
        )
        self._thread.start()

    def enqueue(self, timestamp, relative_time, freq1, freq2, diff):
        """Put one sample into the write queue. Safe to call from any thread."""
        if self._queue is None:
            return
        self._queue.put((timestamp, relative_time, freq1, freq2, diff))
        with self._lock:
            self._row_count += 1

    def close(self):
        """Signal the writer thread to finish, wait for it, and return (filepath, count)."""
        if self._queue is not None:
            self._queue.put(_SENTINEL)

        if self._thread is not None:
            self._thread.join(timeout=5.0)

        filepath = self._filepath
        with self._lock:
            count = self._row_count

        self._queue = None
        self._thread = None
        self._filepath = None
        self._row_count = 0
        return filepath, count

    # --- Writer thread ---

    @staticmethod
    def _writer_loop(filepath, q):
        """Runs in a dedicated thread. Drains the queue and writes to CSV."""
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(HEADER)
            f.flush()

            while True:
                item = q.get()
                if item is _SENTINEL:
                    # Drain any remaining items before exiting
                    while not q.empty():
                        try:
                            remaining = q.get_nowait()
                            if remaining is _SENTINEL:
                                continue
                            _write_row(writer, remaining)
                        except queue.Empty:
                            break
                    f.flush()
                    break

                _write_row(writer, item)
                f.flush()


def _write_row(writer, data):
    """Format and write a single CSV row."""
    timestamp, relative_time, freq1, freq2, diff = data
    writer.writerow([
        timestamp.strftime("%Y-%m-%d"),
        timestamp.strftime("%H:%M:%S.%f")[:-3],
        f"{relative_time:.3f}",
        f"{freq1:.1f}",
        f"{freq2:.1f}",
        f"{diff:.1f}",
    ])
