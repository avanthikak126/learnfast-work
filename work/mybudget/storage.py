from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .account import Account
from .exceptions import BudgetError
from .transaction import Transaction

SCHEMA_VERSION = 1


@dataclass
class LoadResult:
    account: Account
    problems: list[str] = field(default_factory=list)


def save(account: Account, path: str | Path) -> None:
    path = Path(path)

    payload = {
        "version": SCHEMA_VERSION,
        "name": account.name,
        "allow_overdraft": account.allow_overdraft,
        "budgets": {
            category: str(value)
            for category, value in account.budgets.items()
        },
        "transactions": [
            {
                "date": t.date.isoformat(),
                "amount": str(t.amount),
                "category": t.category,
                "description": t.description,
            }
            for t in account.transactions
        ],
    }

    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def load(path: str | Path) -> LoadResult:
    path = Path(path)

    if not path.exists():
        return LoadResult(Account())

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("top level is not an object")

    except (ValueError, UnicodeDecodeError) as exc:
        quarantine = path.with_name(path.name + ".corrupt")
        os.replace(path, quarantine)

        return LoadResult(
            Account(),
            [f"{path.name} was unreadable ({exc}); kept as {quarantine.name}"]
        )

    account = Account(
        name=str(data.get("name", "Main")),
        allow_overdraft=bool(data.get("allow_overdraft", False)),
    )

    problems = []

    for category, limit in (data.get("budgets") or {}).items():
        try:
            account.set_budget(category, Decimal(limit))
        except (InvalidOperation, TypeError, BudgetError) as exc:
            problems.append(f"budget {category!r} skipped: {exc}")

    good = []

    for index, record in enumerate(data.get("transactions") or []):
        try:
            good.append(
                Transaction.parse(
                    record["date"],
                    record["amount"],
                    record["category"],
                    record.get("description", ""),
                )
            )
        except (KeyError, TypeError, AttributeError, BudgetError) as exc:
            problems.append(
                f"transaction #{index} skipped: {exc!r}"
            )

    account.add_many(good, enforce_limits=False)

    return LoadResult(account, problems)
