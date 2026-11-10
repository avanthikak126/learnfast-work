import datetime as dt
from decimal import Decimal

import pytest

from mybudget import (
    Account, BudgetExceededError, InsufficientFundsError,
    InvalidTransactionError, RecurringTransaction, Report,
    StatementImportError, Transaction, load, save,
)
from mybudget.importer import ImportJob, parse_statement


def tx(day, amount, category="misc"):
    return Transaction(
        dt.date.fromisoformat(day), Decimal(amount), category
    )


@pytest.mark.parametrize("amount", ["0", "NaN"])
def test_unusable_amounts_are_refused(amount):
    with pytest.raises(InvalidTransactionError):
        tx("2026-01-01", amount)


def test_money_adds_exactly():
    account = Account()
    for _ in range(1000):
        account.add(tx("2026-01-01", "0.10"))
    assert account.balance == Decimal("100.00")


def test_overdraft_is_refused():
    account = Account()
    account.add(tx("2026-01-01", "100"))

    with pytest.raises(InsufficientFundsError):
        account.add(tx("2026-01-02", "-150"))

    assert account.balance == Decimal("100")


def test_batch_is_all_or_nothing():
    account = Account()
    account.add(tx("2026-01-01", "100"))
    batch = [tx(f"2026-01-0{d}", "-30") for d in (2, 3, 4, 5)]

    with pytest.raises(InsufficientFundsError):
        account.add_many(batch)

    assert len(account.transactions) == 1


def test_budget_limit():
    account = Account()
    account.add(tx("2026-01-01", "1000"))
    account.set_budget("dining", Decimal("100"))
    account.add(tx("2026-01-05", "-60", "dining"))

    with pytest.raises(BudgetExceededError):
        account.add(tx("2026-01-06", "-50", "dining"))


def test_monthly_recurring_transaction():
    bill = RecurringTransaction(
        dt.date(2026, 1, 31), Decimal("-20"), "phone"
    )
    days = [t.date for t in bill.occurrences(dt.date(2026, 3, 31))]

    assert days == [
        dt.date(2026, 1, 31),
        dt.date(2026, 2, 28),
        dt.date(2026, 3, 31),
    ]


def test_report_is_abstract():
    with pytest.raises(TypeError):
        Report()


def test_save_and_load(tmp_path):
    account = Account()
    account.add(tx("2026-01-01", "12.10", "salary"))

    save(account, tmp_path / "b.json")
    loaded = load(tmp_path / "b.json")

    assert loaded.account.transactions == account.transactions


def test_corrupt_file_is_preserved(tmp_path):
    path = tmp_path / "b.json"
    path.write_text("{ not json")

    result = load(path)

    assert result.account.balance == 0
    assert result.problems
    assert (tmp_path / "b.json.corrupt").read_text() == "{ not json"


def test_bad_import_row_reports_line():
    text = (
        "date,description,amount,category\n"
        "2026-01-01,x,5,food\n"
        "2026-01-02,y,oops,food\n"
    )

    with pytest.raises(StatementImportError) as error:
        parse_statement(text)

    assert error.value.line == 3


def test_failed_import_job():
    job = ImportJob()
    job.start(
        "date,description,amount,category\n"
        "2026-01-01,x,oops,food\n"
    )
    job.join(timeout=5)

    assert job.status == "failed"
    assert "line 2" in job.error
    assert job.result is None


class Stop(BaseException):
    pass


@pytest.mark.filterwarnings(
    "ignore::pytest.PytestUnhandledThreadExceptionWarning"
)
def test_worker_stopped_by_baseexception(monkeypatch):
    def die(*args, **kwargs):
        raise Stop()

    monkeypatch.setattr("mybudget.importer.parse_statement", die)

    job = ImportJob()
    job.start("date,description,amount,category\n")
    job.join(timeout=5)

    assert job.status == "failed"
    assert "stopped unexpectedly" in job.error
