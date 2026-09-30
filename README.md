# Personal Expense Tracker

## README
A simple Python command-line application for recording personal expenses, viewing spending summaries, and managing monthly budgets[cite: 3].

---

## 1. Project Overview
The Personal Expense Tracker is a Python-based application designed to make everyday expense management easier and more organised[cite: 3]. Users can create an account, log in, record expenses, view and manage their records, generate monthly reports, set budgets, and export their expenses to a CSV file[cite: 3].

The application stores data locally in an SQLite database, so it can work offline without requiring third-party packages[cite: 3].

---

## 2. Main Features
* **User registration and login**[cite: 3]
* **Secure password hashing** using PBKDF2-SHA256[cite: 3]
* **Expense CRUD operations:** Add, view, update, and delete expenses[cite: 3]
* **Filter expenses** by category[cite: 3]
* **Monthly spending summaries**[cite: 3]
* **Budget setting and budget alerts** at 80% and 100%[cite: 3]
* **Export expenses** to CSV[cite: 3]
* **Input validation** and clear error messages[cite: 3]
* **Logging** of important actions and errors[cite: 3]

---

## 3. Technologies Used
* **Language:** Python 3[cite: 3]
* **Database:** SQLite[cite: 3]
* **Testing:** Python `unittest`[cite: 3]
* **Storage/Export:** SQLite and CSV[cite: 3]
* **Version Control:** Git[cite: 3]

The project uses Python's standard library, which keeps installation simple[cite: 3].

---

## 4. Project Structure
The project is organised into separate modules so that each part has a clear responsibility[cite: 3]:

* `config.py` — Project paths, categories, and configuration[cite: 3]
* `logger.py` — Logging configuration[cite: 4]
* `exceptions.py` — Custom application exceptions[cite: 4]
* `validators.py` — Input validation[cite: 4]
* `models.py` — User and Expense data classes[cite: 4]
* `database.py` — SQLite connection, schema, and database operations[cite: 4]
* `auth.py` — Registration and login[cite: 4]
* `expenses.py` — Adding, viewing, updating, and deleting expenses[cite: 4]
* `reports.py` — Monthly reports, budgets, alerts, and CSV export[cite: 4]
* `cli.py` — Command-line menus and output[cite: 4]
* `main.py` — Program entry point[cite: 4]

---

## 5. How the Application Works
When the program starts, the user can register, log in, or exit[cite: 4]. After logging in, a numbered menu is displayed[cite: 4]. The user can choose an expense-related action, view a monthly report, set a budget, export data, or log out[cite: 4].

Each operation validates the supplied input before interacting with the database[cite: 4]. If an error occurs, the program displays a clear message and returns the user to the menu[cite: 4].

---

## 6. Database
The application uses three main tables[cite: 4]:

* **Users:** Stores user accounts, password hashes, salts, and creation dates[cite: 4].
* **Expenses:** Stores the user ID, amount, category, description, and date[cite: 4].
* **Budgets:** Stores monthly category budgets for each user[cite: 4].

User data is kept separate by associating expenses and budgets with the logged-in user's ID[cite: 4].

---

## 7. Security and Reliability
Passwords are not stored as plain text[cite: 4]. The project uses PBKDF2-SHA256 with a separate salt for each user[cite: 4]. SQL queries use parameter binding, and database operations use transactions so failed operations can be rolled back[cite: 4].

The application also validates input, uses database constraints, logs important actions and errors, and checks CSV export file names[cite: 4].

---

## 8. Testing
The project includes automated unit tests using Python's `unittest` framework[cite: 4]. Tests use a fresh in-memory SQLite database so that testing does not modify real application data[cite: 4].

The project report records 24 tests run, with all 24 tests passing[cite: 4].

Run the tests with:
```bash
python -m unittest discover tests -v
```[cite: 4]

---

## 9. Example Usage
A typical session is:
1. Register an account[cite: 5]
2. Log in[cite: 5]
3. Add expenses[cite: 5]
4. View or filter expenses[cite: 5]
5. Generate a monthly report[cite: 5]
6. Check budget alerts[cite: 5]
7. Export data[cite: 5]
8. Log out[cite: 5]

---

## 10. Future Improvements
* Recurring expenses and reminders[cite: 5]
* Charts and graphical reports[cite: 5]
* PDF and Excel export[cite: 5]
* A web interface using Flask[cite: 5]
* Custom categories[cite: 5]
* Multi-currency support[cite: 5]
* Optional password reset and account lockout[cite: 5]

---

## 11. Conclusion
The Personal Expense Tracker demonstrates practical use of Python programming concepts including modular programming, classes, exception handling, database operations, file handling, logging, and unit testing[cite: 5]. The project provides a simple offline solution for keeping track of personal expenses and budgets[cite: 5].

---

## 12. References
* Python 3 Documentation — Python Software Foundation[cite: 5]
* SQLite Documentation[cite: 5]
* OWASP Password Storage Cheat Sheet[cite: 5]
* Pro Git Book[cite: 5]