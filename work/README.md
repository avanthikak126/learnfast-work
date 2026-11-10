# Budget Tracker

A Python-based personal budget tracker built using Object-Oriented Programming, Streamlit, JSON persistence, and background threading.

## Features

- Add income and expenses
- Exact monetary calculations using Decimal
- Recurring transactions
- Monthly and category reports
- Budget limits and overdraft protection
- JSON persistence and recovery
- CSV bank statement import
- Background import with progress tracking
- Automated tests using pytest

## Technologies Used

- Python
- Streamlit
- Object-Oriented Programming
- JSON
- Threading
- Decimal
- Pytest

## Installation

Clone the repository and navigate to the project folder.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
streamlit run budget_app.py
```

## Run Tests

```bash
python -m pytest -q
```

## CSV Import Format

The bank statement CSV must contain these columns:

```csv
date,description,amount,category
2026-11-01,Monthly Salary,35000,salary
2026-11-02,Groceries,-2500,groceries
```

Positive amounts represent income. Negative amounts represent expenses.

## Design Notes

- Encapsulation protects account state and transaction data.
- Inheritance supports recurring transactions.
- Abstract classes define report interfaces.
- Decimal ensures accurate monetary calculations.
- JSON provides persistent local storage.
- Background threading keeps long-running imports from blocking the interface.
- Locks protect shared import-job state.

## Limitations

This is a local, single-user budget tracker. It does not currently include authentication or multi-user cloud storage.
