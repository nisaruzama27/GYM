from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import uuid
import time

# -----------------------------
# Flask App Initialization
# -----------------------------
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)


# In-memory store for demo subscriptions (reset on server restart)
SUBSCRIPTIONS = []


# -----------------------------
# Database Setup
# -----------------------------
DB_NAME = "gym_app.db"


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        # User table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """
        )
        # Subscription table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL
            )
        """
        )
        conn.commit()


# -----------------------------
# Basic Routes (HTML Pages)
# -----------------------------
@app.route("/")
def home():
    return render_template("indexxx.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/sub")
def sub():
    return render_template("sub.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/cr7")
def cr7():
    return render_template("cr7.html")


@app.route("/getacoach")
def getacoach():
    return render_template("getacoach.html")


@app.route("/strength-training")
def strength_training():
    return render_template("strength-training.html")


@app.route("/body-building")
def body_building():
    return render_template("body-building.html")


# -----------------------------
# API Routes (AJAX / JS calls)
# -----------------------------


# 🔹 User Signup
@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not all([name, email, password]):
        return jsonify({"error": "Missing required fields"}), 400

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        if cur.fetchone():
            return (
                jsonify({"error": "User already exists!"}),
                409,
            )  # Use 409 for conflict

        cur.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password),
        )
        conn.commit()
        # Return the new user's name for immediate login
        return jsonify({"message": "Signup successful!", "user": name}), 201


# 🔹 User Login
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row  # Allows accessing columns by name
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cur.fetchone()

        if user:
            # **FIXED**: Check password correctly from the 'password' column
            if user["password"] == password:
                return (
                    jsonify({"message": "Login successful!", "user": user["name"]}),
                    200,
                )
            else:
                return (
                    jsonify({"error": "Incorrect password"}),
                    401,
                )  # Use 401 for unauthorized
        else:
            return jsonify({"error": "User not found"}), 404


@app.route("/api/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json()
    email = data.get("email")

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM subscriptions WHERE email=?", (email,))
        existing = cur.fetchone()

        if existing:
            return jsonify({"message": "Already subscribed!"}), 200
        else:
            cur.execute("INSERT INTO subscriptions (email) VALUES (?)", (email,))
            conn.commit()
            return jsonify({"message": "Subscribed successfully!"}), 201


@app.route("/api/plans", methods=["POST"])
def plans():
    data = request.get_json()
    plan = data.get("plan")
    payment_method = data.get("payment_method")

    if not plan or not payment_method:
        return jsonify({"error": "Missing plan or payment method"}), 400

    return jsonify(
        {
            "message": f"Successfully subscribed to {plan.capitalize()} plan using {payment_method}!"
        }
    )


@app.route("/api/create_order", methods=["POST"])
def create_order():
    """
    Expects JSON: { "plan": "student" }
    Returns a fake order id and amount (in paise for consistency with real gateways).
    """
    data = request.get_json() or {}
    plan = data.get("plan", "student")
    pricing = {"student": 39900, "individual": 69900, "family": 99900}
    amount = pricing.get(plan, 39900)

    # Create a fake order id
    order_id = "order_fake_" + uuid.uuid4().hex[:12]
    # store minimal info for verification
    SUBSCRIPTIONS.append(
        {
            "order_id": order_id,
            "plan": plan,
            "amount": amount,
            "status": "created",
            "created_at": int(time.time()),
        }
    )

    return jsonify({"ok": True, "order_id": order_id, "amount": amount})


@app.route("/api/verify_payment", methods=["POST"])
def verify_payment():
    """
    Simulate backend verification. Expects JSON:
    { "order_id":"...", "payment_id":"...", "signature":"..." }
    We'll accept anything as "valid" for demo, but we update the in-memory store.
    """
    payload = request.get_json() or {}
    order_id = payload.get("order_id")
    payment_id = payload.get("payment_id") or ("pay_fake_" + uuid.uuid4().hex[:10])

    # find the fake order
    record = next((r for r in SUBSCRIPTIONS if r["order_id"] == order_id), None)
    if not record:
        return jsonify({"ok": False, "error": "Order not found"}), 400

    # Simulate verification (here always succeeds)
    record.update(
        {"payment_id": payment_id, "status": "paid", "verified_at": int(time.time())}
    )

    # In a real app: persist to DB, send confirmation email, grant access, etc.
    return jsonify(
        {"ok": True, "message": "Payment verified (demo).", "payment_id": payment_id}
    )


@app.route("/api/subscriptions", methods=["GET"])
def list_subscriptions():
    """Return the in-memory subscriptions (for demo/testing)."""
    return jsonify({"ok": True, "subscriptions": SUBSCRIPTIONS})


# -----------------------------
# Main Entry
# -----------------------------
if __name__ == "__main__":
    if not os.path.exists(DB_NAME):
        init_db()
    app.run(debug=True)
