from __future__ import annotations

import calendar
import datetime as dt
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from .exceptions import InvalidTransactionError

FREQUENCIES = ("weekly", "monthly")


@dataclass(frozen=True)
class Transaction:
    date: dt.date
    amount: Decimal
    category: str
    description: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.date, dt.date):
            raise InvalidTransactionError(f"date must be a date, got {self.date!r}")
        if not isinstance(self.amount, Decimal) or not self.amount.is_finite():
            raise InvalidTransactionError(
                f"amount must be a finite Decimal, got {self.amount!r}"
            )
        if self.amount == 0:
            raise InvalidTransactionError("amount must not be zero")
        if not self.category.strip():
            raise InvalidTransactionError("category must not be empty")

    @property
    def kind(self) -> str:
        return "income" if self.amount > 0 else "expense"

    def occurrences(self, until: dt.date | None = None) -> list[Transaction]:
        return [self]

    @classmethod
    def parse(cls, date: str, amount: str, category: str,
              description: str = "", **extra):
        try:
            parsed_date = dt.date.fromisoformat(date.strip())
        except ValueError:
            raise InvalidTransactionError(
                f"date must look like 2026-03-15, got {date!r}"
            ) from None

        try:
            parsed_amount = Decimal(amount.strip())
        except InvalidOperation:
            raise InvalidTransactionError(
                f"amount must be a number, got {amount!r}"
            ) from None

        return cls(
            parsed_date,
            parsed_amount,
            category.strip().lower(),
            description.strip(),
            **extra
        )


@dataclass(frozen=True)
class RecurringTransaction(Transaction):
    frequency: str = "monthly"

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.frequency not in FREQUENCIES:
            raise InvalidTransactionError(
                f"frequency must be one of {FREQUENCIES}, got {self.frequency!r}"
            )

    def _nth(self, n: int) -> dt.date:
        if self.frequency == "weekly":
            return self.date + dt.timedelta(weeks=n)

        year_offset, month_index = divmod(self.date.month - 1 + n, 12)
        year, month = self.date.year + year_offset, month_index + 1
        day = min(self.date.day, calendar.monthrange(year, month)[1])
        return dt.date(year, month, day)

    def occurrences(self, until: dt.date | None = None) -> list[Transaction]:
        until = until or self.date
        out = []
        n = 0

        while (when := self._nth(n)) <= until:
            out.append(
                Transaction(when, self.amount, self.category, self.description)
            )
            n += 1

        return out
