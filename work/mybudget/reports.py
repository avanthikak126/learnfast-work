"""Reports (lessons 3-4): abstraction and polymorphism."""

from __future__ import annotations
from abc import ABC, abstractmethod
from collections import defaultdict
from decimal import Decimal
from .account import Account


class Report(ABC):
    title = "Report"

    @abstractmethod
    def generate(self, account: Account) -> list[tuple[str, Decimal]]:
        pass

    def render(self, account: Account) -> str:
        rows = self.generate(account)
        lines = [self.title, "-" * len(self.title)]
        lines += [
            f"{label:<20}{amount:>14,.2f}"
            for label, amount in rows
        ]
        if not rows:
            lines.append("(no transactions)")
        return "\n".join(lines)


class MonthlyReport(Report):
    title = "Net by month"

    def generate(self, account: Account):
        totals = defaultdict(Decimal)
        for t in account.transactions:
            totals[t.date.strftime("%Y-%m")] += t.amount
        return sorted(totals.items())


class CategoryReport(Report):
    title = "Spending by category"

    def generate(self, account: Account):
        totals = defaultdict(Decimal)
        for t in account.transactions:
            if t.amount < 0:
                totals[t.category] += -t.amount
        return sorted(totals.items(), key=lambda row: row[1], reverse=True)
