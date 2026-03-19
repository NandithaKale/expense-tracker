import sqlite3
import random
import string
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = "expenses.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def generate_invite_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

def init_db():
    conn = get_connection()
    c    = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS families (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            invite_code TEXT    NOT NULL UNIQUE
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            username     TEXT    NOT NULL UNIQUE,
            password     TEXT    NOT NULL,
            display_name TEXT    NOT NULL,
            role         TEXT    NOT NULL DEFAULT 'member',
            family_id    INTEGER NOT NULL,
            FOREIGN KEY (family_id) REFERENCES families(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            family_id    INTEGER NOT NULL,
            name         TEXT    NOT NULL,
            amount       REAL    NOT NULL,
            category     TEXT    NOT NULL,
            expense_type TEXT    NOT NULL DEFAULT 'personal',
            tag          TEXT    DEFAULT '',
            date         TEXT    NOT NULL,
            FOREIGN KEY (user_id)   REFERENCES users(id),
            FOREIGN KEY (family_id) REFERENCES families(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS income (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id   INTEGER NOT NULL,
            family_id INTEGER NOT NULL,
            amount    REAL    NOT NULL,
            category  TEXT    NOT NULL,
            note      TEXT    DEFAULT '',
            month     TEXT    NOT NULL,
            FOREIGN KEY (user_id)   REFERENCES users(id),
            FOREIGN KEY (family_id) REFERENCES families(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS budget (
            id        INTEGER PRIMARY KEY,
            user_id   INTEGER NOT NULL UNIQUE,
            family_id INTEGER NOT NULL,
            amount    REAL    NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id)   REFERENCES users(id),
            FOREIGN KEY (family_id) REFERENCES families(id)
        )
    ''')

    conn.commit()
    conn.close()

# ── Families ──────────────────────────────────────────────────

def create_family(name):
    conn = get_connection()
    code = generate_invite_code()
    # keep generating until unique
    while conn.execute("SELECT id FROM families WHERE invite_code=?", (code,)).fetchone():
        code = generate_invite_code()
    conn.execute("INSERT INTO families (name, invite_code) VALUES (?,?)", (name, code))
    conn.commit()
    family_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return family_id, code

def get_family_by_invite_code(code):
    conn = get_connection()
    row  = conn.execute("SELECT * FROM families WHERE invite_code=?", (code.upper(),)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_family_by_id(family_id):
    conn = get_connection()
    row  = conn.execute("SELECT * FROM families WHERE id=?", (family_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

# ── Users ─────────────────────────────────────────────────────

def create_user(username, password, display_name, role, family_id):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username,password,display_name,role,family_id) VALUES (?,?,?,?,?)",
            (username, generate_password_hash(password), display_name, role, family_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_by_username(username):
    conn = get_connection()
    row  = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None

def verify_user(username, password):
    user = get_user_by_username(username)
    if user and check_password_hash(user["password"], password):
        return user
    return None

def get_all_users_in_family(family_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, username, display_name, role, family_id FROM users WHERE family_id=?",
        (family_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_user_by_id(user_id):
    conn = get_connection()
    row  = conn.execute(
        "SELECT id, username, display_name, role, family_id FROM users WHERE id=?",
        (user_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

# ── Expenses ──────────────────────────────────────────────────

def get_expenses(family_id, user_id=None, expense_type=None):
    conn  = get_connection()
    query = """
        SELECT
            e.id           AS id,
            e.user_id      AS user_id,
            e.family_id    AS family_id,
            e.name         AS name,
            e.amount       AS amount,
            e.category     AS category,
            e.expense_type AS expense_type,
            e.tag          AS tag,
            e.date         AS date,
            u.display_name AS member_name
        FROM expenses e
        JOIN users u ON e.user_id = u.id
        WHERE e.family_id = ?
    """
    params = [family_id]
    if user_id:
        query += " AND e.user_id = ?"
        params.append(user_id)
    if expense_type:
        query += " AND e.expense_type = ?"
        params.append(expense_type)
    query += " ORDER BY e.date DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_expense(user_id, family_id, name, amount, category, expense_type, tag, date):
    conn = get_connection()
    conn.execute(
        "INSERT INTO expenses (user_id,family_id,name,amount,category,expense_type,tag,date) VALUES (?,?,?,?,?,?,?,?)",
        (user_id, family_id, name, amount, category, expense_type, tag, date)
    )
    conn.commit()
    conn.close()

def delete_expense(expense_id, user_id, role, family_id):
    conn = get_connection()
    if role == "admin":
        conn.execute(
            "DELETE FROM expenses WHERE id=? AND family_id=?",
            (expense_id, family_id)
        )
    else:
        conn.execute(
            "DELETE FROM expenses WHERE id=? AND user_id=? AND family_id=?",
            (expense_id, user_id, family_id)
        )
    conn.commit()
    conn.close()

def update_expense(expense_id, user_id, role, family_id, name, amount, category, expense_type, tag, date):
    conn = get_connection()
    if role == "admin":
        conn.execute(
            "UPDATE expenses SET name=?,amount=?,category=?,expense_type=?,tag=?,date=? WHERE id=? AND family_id=?",
            (name, amount, category, expense_type, tag, date, expense_id, family_id)
        )
    else:
        conn.execute(
            "UPDATE expenses SET name=?,amount=?,category=?,expense_type=?,tag=?,date=? WHERE id=? AND user_id=? AND family_id=?",
            (name, amount, category, expense_type, tag, date, expense_id, user_id, family_id)
        )
    conn.commit()
    conn.close()

# ── Income ────────────────────────────────────────────────────

def get_income(family_id, user_id=None, month=None):
    conn  = get_connection()
    query = """
        SELECT
            i.id           AS id,
            i.user_id      AS user_id,
            i.family_id    AS family_id,
            i.amount       AS amount,
            i.category     AS category,
            i.note         AS note,
            i.month        AS month,
            u.display_name AS member_name
        FROM income i
        JOIN users u ON i.user_id = u.id
        WHERE i.family_id = ?
    """
    params = [family_id]
    if user_id:
        query += " AND i.user_id = ?"
        params.append(user_id)
    if month:
        query += " AND i.month = ?"
        params.append(month)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_income(user_id, family_id, amount, category, note, month):
    conn = get_connection()
    conn.execute(
        "INSERT INTO income (user_id,family_id,amount,category,note,month) VALUES (?,?,?,?,?,?)",
        (user_id, family_id, amount, category, note, month)
    )
    conn.commit()
    conn.close()

def delete_income(income_id, user_id, role, family_id):
    conn = get_connection()
    if role == "admin":
        conn.execute(
            "DELETE FROM income WHERE id=? AND family_id=?",
            (income_id, family_id)
        )
    else:
        conn.execute(
            "DELETE FROM income WHERE id=? AND user_id=? AND family_id=?",
            (income_id, user_id, family_id)
        )
    conn.commit()
    conn.close()

# ── Budget ────────────────────────────────────────────────────

def get_budget(user_id):
    conn = get_connection()
    row  = conn.execute("SELECT amount FROM budget WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return row["amount"] if row else 0

def set_budget(user_id, family_id, amount):
    conn = get_connection()
    conn.execute(
        "INSERT INTO budget (user_id,family_id,amount) VALUES (?,?,?) ON CONFLICT(user_id) DO UPDATE SET amount=?",
        (user_id, family_id, amount, amount)
    )
    conn.commit()
    conn.close()

# ── Summary ───────────────────────────────────────────────────

def get_category_totals(family_id, user_id=None):
    conn = get_connection()
    if user_id:
        rows = conn.execute(
            "SELECT category, SUM(amount) as total FROM expenses WHERE family_id=? AND user_id=? GROUP BY category",
            (family_id, user_id)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT category, SUM(amount) as total FROM expenses WHERE family_id=? GROUP BY category",
            (family_id,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_monthly_totals(family_id, user_id=None):
    conn = get_connection()
    if user_id:
        rows = conn.execute(
            """SELECT strftime('%Y-%m', date) as month, SUM(amount) as total
               FROM expenses WHERE family_id=? AND user_id=?
               GROUP BY month ORDER BY month DESC LIMIT 6""",
            (family_id, user_id)
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT strftime('%Y-%m', date) as month, SUM(amount) as total
               FROM expenses WHERE family_id=?
               GROUP BY month ORDER BY month DESC LIMIT 6""",
            (family_id,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_family_summary(family_id):
    conn = get_connection()
    rows = conn.execute(
        """SELECT u.display_name, u.id,
           COALESCE(SUM(e.amount),0) as total_expenses
           FROM users u
           LEFT JOIN expenses e ON u.id=e.user_id AND e.family_id=?
           WHERE u.family_id=?
           GROUP BY u.id""",
        (family_id, family_id)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_family_income_summary(family_id, month=None):
    conn = get_connection()
    if month:
        rows = conn.execute(
            """SELECT u.display_name, u.id,
               COALESCE(SUM(i.amount),0) as total_income
               FROM users u
               LEFT JOIN income i ON u.id=i.user_id AND i.family_id=? AND i.month=?
               WHERE u.family_id=?
               GROUP BY u.id""",
            (family_id, month, family_id)
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT u.display_name, u.id,
               COALESCE(SUM(i.amount),0) as total_income
               FROM users u
               LEFT JOIN income i ON u.id=i.user_id AND i.family_id=?
               WHERE u.family_id=?
               GROUP BY u.id""",
            (family_id, family_id)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]