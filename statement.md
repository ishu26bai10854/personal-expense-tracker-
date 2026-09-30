# Project Statement & Scope

## 1. Problem Statement
Students and young professionals often learn to manage money only after they overspend[cite: 1]. Expenses are usually tracked in memory or on scattered notes, which leads to three common problems[cite: 1]:

* **Scattered Records:** Spending is written in different apps, chats, and notebooks, so there is no single, reliable record of where the money went[cite: 1].
* **No Category-Wise Insight:** Without monthly totals per category, it is hard to see which habits (food, transport, bills, shopping) take the largest share of the budget[cite: 1].
* **No Early Budget Warning:** People usually notice that a monthly budget is exceeded only after the month has ended, when it is too late to change behaviour[cite: 1].

This project addresses these challenges by offering a lightweight, secure, test-driven, and offline-capable Python CLI application backed by a local SQLite database[cite: 1].

---

## 2. Scope of the Project

### In-Scope
* **Secure Multi-User Accounts:** Registration and login with unique usernames; passwords are hashed with PBKDF2-SHA256 and a random per-user salt, and every query is scoped to the logged-in user[cite: 1].
* **Expense Management (CRUD):** Adding, listing (with optional category filter), updating, and deleting expenses with amount, category, date, and description[cite: 1].
* **Monthly Reports:** Category-wise monthly summaries with totals, percentages, and text bars[cite: 1].
* **Budget Alerts:** Setting a monthly limit per category and receiving warnings at 80% and alerts at 100% of the limit[cite: 1].
* **CSV Export:** Exporting all of a user's expenses to a CSV file, with protection against path traversal and spreadsheet-formula injection[cite: 1].
* **Local Data Persistence:** Storing users, expenses, and budgets in a local SQLite database (`data/expenses.db`) with transactions, foreign keys, and `CHECK` constraints[cite: 1].
* **Input Validation & Logging:** Validating every input, handling errors gracefully with custom exceptions, and writing activity to `logs/app.log`[cite: 2].
* **Test-Driven Verification:** Unit testing the core logic with Python's `unittest` framework using an in-memory database[cite: 2].

### Out-of-Scope
* Web or mobile user interface (strictly CLI-based)[cite: 2].
* Bank or payment-app integration (no automatic import of transactions)[cite: 2].
* Multi-currency support and custom categories (a fixed category list is used)[cite: 2].
* Cloud database hosting or synchronisation between devices[cite: 2].

---

## 3. Target Users
* **Students & Young Professionals:** Users who want a private, offline tool to record daily spending, understand their habits, and stay within a monthly budget[cite: 2].
* **Evaluators & Learners:** Anyone reviewing the project as an example of layered Python design (interface, services, storage) using only the standard library[cite: 2].

---

## 4. High-Level Features
* **User Management Engine:** Secure registration and login with salted, hashed passwords and constant-time comparison[cite: 2].
* **Expense Management Engine:** Validated add, view, filter, update, and delete operations isolated per user[cite: 2].
* **Reporting & Budget Engine:** SQL-based monthly aggregation, category percentages, and budget threshold alerts at 80% / 100%[cite: 2].
* **SQLite Storage Handler:** Transaction-safe persistence of all records across CLI sessions[cite: 2].
* **CSV Export Handler:** Safe export of expense history for use in spreadsheets[cite: 2].
* **Automated Test Suite:** 24 unit tests validating input handling, authentication, expense logic, reports, and data isolation[cite: 2].