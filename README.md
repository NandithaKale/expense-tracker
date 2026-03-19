# 💸 Family Expense Tracker

A full-stack web app for families to track expenses and income together.
Built with Python Flask, SQLite, and a dark mode dashboard UI.

---

## 🚀 Tech Stack

| Layer      | Technology                  |
|------------|-----------------------------|
| Backend    | Python + Flask              |
| Database   | SQLite                      |
| Frontend   | HTML + CSS + Vanilla JS     |
| Charts     | Chart.js                    |
| Auth       | Werkzeug + Flask Sessions   |

---

## 📁 Project Structure
```
expense-tracker/
├── app.py               ← Flask server & API routes
├── database.py          ← All database queries
├── models.py            ← Python data models
├── requirements.txt     ← Python dependencies
├── expenses.db          ← SQLite DB (auto created)
├── static/
│   ├── style.css        ← Dark mode UI styles
│   └── app.js           ← Frontend JavaScript
└── templates/
    ├── login.html       ← Login & Register page
    └── dashboard.html   ← Main dashboard
```

---

## ⚙️ Setup & Run

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Run the app**
```bash
python app.py
```

**3. Open in browser**
```
http://127.0.0.1:5000
```

---

## 🔐 First Time Use

1. Go to `/login` and click **Register**
2. Enter your name, username and password
3. Choose **Create a Family** and give it a name
4. You will get a **6-character invite code** — share it with family members
5. Other members register using **Join a Family** and enter the invite code

---

## ✨ Features

- **Authentication** — Secure login with hashed passwords, 7-day sessions
- **Family Groups** — Invite code system to group family members together
- **Expenses** — Add, delete and filter by category or member
- **Income** — Track monthly income per member with categories
- **Budget** — Set monthly budget with a live progress bar
- **Charts** — Doughnut chart for categories, bar chart for 6 month trend
- **Family Overview** — See every member's income vs expenses side by side
- **Roles** — Admin can manage all entries, members manage their own

---

## 🗄️ Database Tables

| Table      | Purpose                              |
|------------|--------------------------------------|
| families   | Family groups and invite codes       |
| users      | Members, passwords, roles            |
| expenses   | All expense entries                  |
| income     | All income entries                   |
| budget     | Monthly budget per member            |

---

## 📦 Dependencies
```
flask
flask-cors
werkzeug
```

Install with:
```bash
pip install -r requirements.txt
```

---

## 🛠️ Reset Database
```bash
del expenses.db
python app.py
```

---

## 📌 Notes

- The `expenses.db` file is created automatically on first run
- Only the family admin can see the invite code in the Family tab
- Admins can delete any member's entries, members can only delete their own
