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

The database will be recreated automatically.

---

## Notes

- The database file is created automatically the first time you run the app
- Only the family admin can see the invite code in the Family tab
- Admins can delete any entry, members can only delete their own
