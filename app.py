from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from datetime import timedelta
import database as db

app = Flask(__name__)
app.secret_key = "expense_tracker_super_secret_key_2024"
app.config["SESSION_COOKIE_SAMESITE"]      = "Lax"
app.config["SESSION_COOKIE_SECURE"]        = False
app.config["SESSION_COOKIE_HTTPONLY"]      = True
app.config["PERMANENT_SESSION_LIFETIME"]   = timedelta(days=7)
CORS(app, supports_credentials=True)
db.init_db()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# ── Pages ─────────────────────────────────────────────────────

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    return render_template("dashboard.html")

@app.route("/login")
def login_page():
    if "user_id" in session:
        return redirect(url_for("index"))
    return render_template("login.html")

# ── Auth ──────────────────────────────────────────────────────

@app.route("/api/auth/register", methods=["POST"])
def register():
    body         = request.get_json()
    username     = body.get("username",     "").strip()
    password     = body.get("password",     "").strip()
    display_name = body.get("display_name", "").strip()
    action       = body.get("action",       "join")   # "create" or "join"
    family_name  = body.get("family_name",  "").strip()
    invite_code  = body.get("invite_code",  "").strip().upper()

    if not username or not password or not display_name:
        return jsonify({"error": "All fields are required"}), 400
    if len(password) < 4:
        return jsonify({"error": "Password must be at least 4 characters"}), 400

    if action == "create":
        if not family_name:
            return jsonify({"error": "Family name is required"}), 400
        family_id, code = db.create_family(family_name)
        role = "admin"
    else:
        if not invite_code:
            return jsonify({"error": "Invite code is required"}), 400
        family = db.get_family_by_invite_code(invite_code)
        if not family:
            return jsonify({"error": "Invalid invite code"}), 404
        family_id = family["id"]
        role      = "member"

    success = db.create_user(username, password, display_name, role, family_id)
    if not success:
        return jsonify({"error": "Username already exists"}), 409

    if action == "create":
        return jsonify({"message": "Family created! Your invite code is: " + code, "invite_code": code}), 201
    return jsonify({"message": "Joined family successfully!"}), 201

@app.route("/api/auth/login", methods=["POST"])
def login():
    body     = request.get_json()
    username = body.get("username", "").strip()
    password = body.get("password", "").strip()
    user     = db.verify_user(username, password)
    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    session.permanent        = True
    session["user_id"]       = int(user["id"])
    session["display_name"]  = user["display_name"]
    session["role"]          = user["role"]
    session["family_id"]     = int(user["family_id"])

    family = db.get_family_by_id(int(user["family_id"]))

    return jsonify({
        "message":      "Login successful",
        "user_id":      int(user["id"]),
        "display_name": user["display_name"],
        "role":         user["role"],
        "family_id":    int(user["family_id"]),
        "family_name":  family["name"]       if family else "",
        "invite_code":  family["invite_code"] if family else ""
    })

@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})

@app.route("/api/auth/me", methods=["GET"])
@login_required
def me():
    family = db.get_family_by_id(int(session["family_id"]))
    return jsonify({
        "user_id":      int(session["user_id"]),
        "display_name": session["display_name"],
        "role":         session["role"],
        "family_id":    int(session["family_id"]),
        "family_name":  family["name"]        if family else "",
        "invite_code":  family["invite_code"] if family else ""
    })

# ── Users ─────────────────────────────────────────────────────

@app.route("/api/users", methods=["GET"])
@login_required
def get_users():
    return jsonify(db.get_all_users_in_family(int(session["family_id"])))

# ── Expenses ──────────────────────────────────────────────────

@app.route("/api/expenses", methods=["GET"])
@login_required
def get_expenses():
    uid          = request.args.get("user_id",  type=int)
    expense_type = request.args.get("type")
    return jsonify(db.get_expenses(int(session["family_id"]), uid, expense_type))

@app.route("/api/expenses", methods=["POST"])
@login_required
def add_expense():
    body = request.get_json()
    for f in ["name", "amount", "category", "date"]:
        if not body.get(f):
            return jsonify({"error": f"{f} is required"}), 400
    try:
        amount = float(body["amount"])
        if amount <= 0:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Amount must be positive"}), 400
    db.add_expense(
        user_id      = int(session["user_id"]),
        family_id    = int(session["family_id"]),
        name         = body["name"],
        amount       = amount,
        category     = body["category"],
        expense_type = body.get("expense_type", "personal"),
        tag          = body.get("tag", ""),
        date         = body["date"]
    )
    return jsonify({"message": "Expense added"}), 201

@app.route("/api/expenses/<int:expense_id>", methods=["DELETE"])
@login_required
def delete_expense(expense_id):
    db.delete_expense(expense_id, int(session["user_id"]), session["role"], int(session["family_id"]))
    return jsonify({"message": "Deleted"})

@app.route("/api/expenses/<int:expense_id>", methods=["PUT"])
@login_required
def update_expense(expense_id):
    body = request.get_json()
    db.update_expense(
        expense_id   = expense_id,
        user_id      = int(session["user_id"]),
        role         = session["role"],
        family_id    = int(session["family_id"]),
        name         = body["name"],
        amount       = float(body["amount"]),
        category     = body["category"],
        expense_type = body.get("expense_type", "personal"),
        tag          = body.get("tag", ""),
        date         = body["date"]
    )
    return jsonify({"message": "Updated"})

# ── Income ────────────────────────────────────────────────────

@app.route("/api/income", methods=["GET"])
@login_required
def get_income():
    uid   = request.args.get("user_id", type=int)
    month = request.args.get("month")
    return jsonify(db.get_income(int(session["family_id"]), uid, month))

@app.route("/api/income", methods=["POST"])
@login_required
def add_income():
    body = request.get_json()
    try:
        amount = float(body["amount"])
        if amount <= 0:
            raise ValueError
    except (ValueError, KeyError):
        return jsonify({"error": "Valid amount required"}), 400
    if not body.get("month"):
        return jsonify({"error": "Month is required"}), 400
    db.add_income(
        user_id   = int(session["user_id"]),
        family_id = int(session["family_id"]),
        amount    = amount,
        category  = body.get("category", "Salary"),
        note      = body.get("note", ""),
        month     = body["month"]
    )
    return jsonify({"message": "Income added"}), 201

@app.route("/api/income/<int:income_id>", methods=["DELETE"])
@login_required
def delete_income(income_id):
    db.delete_income(income_id, int(session["user_id"]), session["role"], int(session["family_id"]))
    return jsonify({"message": "Deleted"})

# ── Budget ────────────────────────────────────────────────────

@app.route("/api/budget", methods=["GET"])
@login_required
def get_budget():
    uid = request.args.get("user_id", type=int) or int(session["user_id"])
    return jsonify({"budget": db.get_budget(uid)})

@app.route("/api/budget", methods=["POST"])
@login_required
def set_budget():
    body = request.get_json()
    try:
        amount = float(body["amount"])
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid amount"}), 400
    db.set_budget(int(session["user_id"]), int(session["family_id"]), amount)
    return jsonify({"message": "Budget set"})

# ── Summary ───────────────────────────────────────────────────

@app.route("/api/summary/categories", methods=["GET"])
@login_required
def category_totals():
    uid = request.args.get("user_id", type=int)
    return jsonify(db.get_category_totals(int(session["family_id"]), uid))

@app.route("/api/summary/monthly", methods=["GET"])
@login_required
def monthly_totals():
    uid = request.args.get("user_id", type=int)
    return jsonify(db.get_monthly_totals(int(session["family_id"]), uid))

@app.route("/api/summary/family", methods=["GET"])
@login_required
def family_summary():
    fid        = int(session["family_id"])
    month      = request.args.get("month")
    expenses   = db.get_family_summary(fid)
    income     = db.get_family_income_summary(fid, month)
    income_map = {r["id"]: r["total_income"] for r in income}
    for member in expenses:
        member["total_income"] = income_map.get(member["id"], 0)
        member["net"]          = member["total_income"] - member["total_expenses"]
    return jsonify(expenses)

if __name__ == "__main__":
    app.run(debug=True)