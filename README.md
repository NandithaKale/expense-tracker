# Family Expense Tracker

A web app for families to track their expenses and income together.
Built with Python Flask and SQLite, with a dark mode dashboard interface.

---

## Tech Stack

| Layer      | Technology                  |
|------------|-----------------------------|
| Backend    | Python + Flask              |
| Database   | SQLite                      |
| Frontend   | HTML, CSS, Vanilla JS       |
| Charts     | Chart.js                    |
| Auth       | Werkzeug + Flask Sessions   |

---

## Project Structure
```
expense-tracker/
├── app.py               Flask server and API routes
├── database.py          Database queries
├── models.py            Data models
├── requirements.txt     Python dependencies
├── expenses.db          SQLite database, auto created on first run
├── static/
│   ├── style.css        Styles
│   └── app.js           Frontend logic
└── templates/
    ├── login.html       Login and register page
    └── dashboard.html   Main dashboard
```

---

## Getting Started

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the app:
```bash
python app.py
```

Open your browser and go to:
```
http://127.0.0.1:5000
```

---

## First Time Setup

1. Go to the login page and click Register
2. Enter your name, username and password
3. Choose Create a Family and give it a name
4. You will get a 6 character invite code — share it with your family members
5. Other members register by choosing Join a Family and entering the code

---

## Features

- Secure login with hashed passwords and 7 day persistent sessions
- Family group system using invite codes — each family's data is completely separate
- Add and delete expenses with categories, types, tags and dates
- Track monthly income per member with income categories
- Set a monthly budget with a live progress bar that warns when you are close to the limit
- Charts showing spending by category and a 6 month spending trend
- Family overview showing each member's income and expenses side by side
- Admin and member roles — admins can manage all entries, members manage their own

---

## Database Tables

| Table      | Purpose                                    |
|------------|--------------------------------------------|
| families   | Stores family groups and invite codes      |
| users      | Stores members, hashed passwords and roles |
| expenses   | All expense entries                        |
| income     | All income entries                         |
| budget     | Monthly budget limit per member            |

---

## Resetting the Database

If you need to start fresh, stop the server and run:
```bash
del expenses.db
python app.py
```

## Screenshots

### Register
<img width="600" alt="Register" src="https://github.com/user-attachments/assets/c49309e5-965a-4741-af98-19c4a46a7e28" />

### Login
<img width="600" alt="Login" src="https://github.com/user-attachments/assets/f1416b5c-9718-49f5-8678-94934265e544" />

### Overview Dashboard
<img width="900" alt="Overview" src="https://github.com/user-attachments/assets/a84bbe13-d9fa-4716-ae73-b7c1e93502cf" />

### Overview with Charts
<img width="900" alt="Overview Charts" src="https://github.com/user-attachments/assets/3f3931a0-de50-4c28-ab3b-c74bfb4dbb98" />

### Expenses
<img width="900" alt="Expenses" src="https://github.com/user-attachments/assets/1cc7d3c5-da27-45f2-92fb-8a3708a0b248" />

### All Family Expenses
<img width="900" alt="All Expenses" src="https://github.com/user-attachments/assets/fad97710-9d58-4559-b295-39b63d3ba236" />

### Income
<img width="900" alt="Income" src="https://github.com/user-attachments/assets/db901879-f614-4ff4-a946-74c5364521c7" />

### Income Two Members
<img width="900" alt="Income Two Members" src="https://github.com/user-attachments/assets/2c04e922-a41d-427a-b4e5-f41af5c92e9e" />

### Family Overview
<img width="900" alt="Family" src="https://github.com/user-attachments/assets/f6a879c0-6b68-4197-90ee-dcd0ef68cc8f" />

The database will be recreated automatically.

---

## Notes

- The database file is created automatically the first time you run the app
- Only the family admin can see the invite code in the Family tab
- Admins can delete any entry, members can only delete their own



