
from __future__ import annotations

import datetime as dt
import os
import time

import streamlit as st

from mybudget import (
    Account, BudgetError, CategoryReport, MonthlyReport,
    RecurringTransaction, Transaction, load, save,
)
from mybudget.importer import ImportJob

SAVE_PATH = os.environ.get("THILIBUDGET_SAVE", "budget.json")

REPORTS = {
    "Net by month": MonthlyReport(),
    "Spending by category": CategoryReport()
}

st.set_page_config(page_title="Budget Tracker", page_icon="💰")
st.title("Budget Tracker")

# Session state
if "account" not in st.session_state:
    result = load(SAVE_PATH)
    st.session_state.account = result.account
    st.session_state.load_problems = result.problems
    st.session_state.job = ImportJob()

account: Account = st.session_state.account

for problem in st.session_state.get("load_problems", []):
    st.warning(problem)

if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

# Add transaction
with st.sidebar:
    st.header("Add a transaction")

    with st.form("add", clear_on_submit=True):
        when = st.date_input("Date", dt.date.today())
        kind = st.radio("Type", ["expense", "income"], horizontal=True)
        amount = st.text_input("Amount", placeholder="12.50")
        category = st.text_input("Category", placeholder="groceries")
        description = st.text_input("Description")
        repeat = st.selectbox("Repeats", ["no", "weekly", "monthly"])

        until = (
            st.date_input("...until", dt.date.today())
            if repeat != "no" else None
        )

        submitted = st.form_submit_button("Add")

    if submitted:
        try:
            signed = ("-" if kind == "expense" else "") + amount.strip()

            if repeat == "no":
                tx = Transaction.parse(
                    when.isoformat(), signed, category, description
                )
            else:
                tx = RecurringTransaction.parse(
                    when.isoformat(), signed, category,
                    description, frequency=repeat
                )

            added = account.add(tx, until=until)

        except BudgetError as exc:
            st.error(str(exc))

        else:
            save(account, SAVE_PATH)
            st.success(f"Added {len(added)} transaction(s).")

# Account display
st.metric("Balance", f"{account.balance:,.2f}")

if account.transactions:
    st.dataframe([
        {
            "date": t.date,
            "amount": float(t.amount),
            "category": t.category,
            "description": t.description
        }
        for t in reversed(account.transactions)
    ])
else:
    st.info("No transactions yet.")

choice = st.selectbox("Report", list(REPORTS))
st.code(REPORTS[choice].render(account))

# Background import
st.header("Import a bank statement")

upload = st.file_uploader(
    "CSV with columns: date, description, amount, category",
    type="csv"
)

job: ImportJob = st.session_state.job
status = job.status

if upload is not None and status != "running" and st.button("Import"):
    job.start(
        upload.getvalue().decode("utf-8", errors="replace"),
        throttle=0.05
    )
    st.rerun()

if status == "running":
    st.progress(job.progress, text="Importing...")
    time.sleep(0.3)
    st.rerun()

elif status == "done":
    rows = job.result or []

    account.add_many(rows, enforce_limits=False)
    save(account, SAVE_PATH)

    job.reset()
    st.session_state["flash"] = f"Imported {len(rows)} transactions."
    st.rerun()

elif status == "failed":
    st.error(f"Import failed — {job.error}")

    if st.button("Dismiss"):
        job.reset()
        st.rerun()
