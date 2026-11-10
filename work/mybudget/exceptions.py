from decimal import Decimal


class BudgetError(Exception):
    """Base class for application errors."""


class InvalidTransactionError(BudgetError, ValueError):
    pass


class InsufficientFundsError(BudgetError):
    def __init__(self, balance: Decimal, needed: Decimal):
        self.balance = balance
        self.needed = needed
        super().__init__(
            f"balance {balance:,.2f} cannot cover an expense of {needed:,.2f}"
        )


class BudgetExceededError(BudgetError):
    def __init__(self, category: str, limit: Decimal, would_be: Decimal):
        self.category = category
        self.limit = limit
        self.would_be = would_be
        super().__init__(
            f"'{category}' budget is {limit:,.2f} this month; "
            f"this would make it {would_be:,.2f}"
        )


class StatementImportError(BudgetError):
    def __init__(self, message: str, line: int | None = None):
        self.line = line
        super().__init__(f"line {line}: {message}" if line else message)
