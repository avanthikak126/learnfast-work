
from __future__ import annotations

import csv
import threading
import time
from collections.abc import Callable

from .exceptions import BudgetError, StatementImportError
from .transaction import Transaction

REQUIRED_COLUMNS = ("date", "description", "amount", "category")
BATCH = 500


def parse_statement(text, on_progress=None, throttle=0.0):
    lines = text.splitlines()

    if not lines:
        raise StatementImportError("the file is empty")

    reader = csv.DictReader(lines)

    missing = [
        c for c in REQUIRED_COLUMNS
        if c not in (reader.fieldnames or [])
    ]

    if missing:
        raise StatementImportError(
            f"missing column(s): {', '.join(missing)}",
            line=1
        )

    total = max(len(lines) - 1, 1)
    out = []

    for done, row in enumerate(reader, start=1):
        line_no = reader.line_num

        if None in row or None in row.values():
            raise StatementImportError(
                "wrong number of columns",
                line=line_no
            )

        try:
            out.append(Transaction.parse(
                row["date"],
                row["amount"],
                row["category"],
                row["description"]
            ))
        except BudgetError as exc:
            raise StatementImportError(
                str(exc), line=line_no
            ) from exc

        if done % BATCH == 0:
            if on_progress:
                on_progress(done / total)
            if throttle:
                time.sleep(throttle)

    if on_progress:
        on_progress(1.0)

    return out


class ImportJob:

    def __init__(self):
        self._lock = threading.Lock()
        self._thread = None
        self._reset()

    def _reset(self):
        self._status = "idle"
        self._progress = 0.0
        self._result = None
        self._error = None

    @property
    def status(self):
        with self._lock:
            return self._status

    @property
    def progress(self):
        with self._lock:
            return self._progress

    @property
    def result(self):
        with self._lock:
            return self._result

    @property
    def error(self):
        with self._lock:
            return self._error

    def reset(self):
        with self._lock:
            self._reset()

    def start(self, text, throttle=0.0):
        with self._lock:
            if self._status == "running":
                raise RuntimeError("an import is already running")

            self._reset()
            self._status = "running"

        self._thread = threading.Thread(
            target=self._run,
            args=(text, throttle),
            daemon=True
        )

        self._thread.start()
        return self._thread

    def join(self, timeout=None):
        if self._thread is not None:
            self._thread.join(timeout)

    def _set_progress(self, value):
        with self._lock:
            self._progress = value

    def _run(self, text, throttle):
        try:
            result = parse_statement(
                text,
                self._set_progress,
                throttle
            )

            with self._lock:
                self._result = result
                self._status = "done"

        except Exception as exc:
            with self._lock:
                self._error = f"{type(exc).__name__}: {exc}"
                self._status = "failed"

        finally:
            with self._lock:
                if self._status == "running":
                    self._error = "the import worker stopped unexpectedly"
                    self._status = "failed"
