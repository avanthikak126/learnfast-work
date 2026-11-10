from __future__ import annotations
import datetime as dt
from collections import defaultdict
from decimal import Decimal

from .exceptions import (
    BudgetExceededError,
    InsufficientFundsError,
    InvalidTransactionError,
)
from .transaction import Transaction


class Account:
    def __init__(self, name="Main", allow_overdraft=False):
        self.name = name
        self.allow_overdraft = allow_overdraft
        self._transactions = []
        self._budgets = {}

    @property
    def balance(self):
        return sum(
            (t.amount for t in self._transactions),
            Decimal("0")
        )

    @property
    def transactions(self):
        return tuple(self._transactions)

    @property
    def budgets(self):
        return dict(self._budgets)

    def spent(self, category, year, month):
        return sum(
            (
                -t.amount for t in self._transactions
                if t.category == category
                and t.amount < 0
                and (t.date.year, t.date.month) == (year, month)
            ),
            Decimal("0")
        )

    def set_budget(self, category, monthly_limit):
        if monthly_limit <= 0:
            raise InvalidTransactionError("a budget limit must be positive")
        self._budgets[category.strip().lower()] = monthly_limit

    def add(self, transaction, until=None):
        return self.add_many(
            transaction.occurrences(until),
            enforce_limits=True
        )

    def add_many(self, transactions, *, enforce_limits=True):
        batch = sorted(transactions, key=lambda t: t.date)

        if enforce_limits:
            self._check(batch)

        self._transactions.extend(batch)
        return batch

    def _check(self, batch):
        balance = self.balance
        spent = defaultdict(Decimal)

        for t in batch:
            balance += t.amount

            if balance < 0 and not self.allow_overdraft:
                raise InsufficientFundsError(
                    balance - t.amount, -t.amount
                )

            if t.amount < 0:
                key = (t.category, t.date.year, t.date.month)

                if key not in spent:
                    spent[key] = self.spent(*key)

                spent[key] += -t.amount
                limit = self._budgets.get(t.category)

                if limit is not None and spent[key] > limit:
                    raise BudgetExceededError(
                        t.category, limit, spent[key]
                    )
