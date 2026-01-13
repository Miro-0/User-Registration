from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret_change_in_prod")  # Secure secret from env

# ===================== DATABASE CONFIG =====================
DATABASE_URL = os.getenv("DATABASE_URL")  # Railway provides DATABASE_URL for PostgreSQL/MySQL
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable not set!")

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ===================== DATABASE MODEL =====================
class User(db.Model):
    __tablename__ = "user"  # Ensures the table is exactly 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    gender = db.Column(db.String(10))
    birthday = db.Column(db.Date)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(100))
    password = db.Column(db.String(255), nullable=False)

# ===================== ROUTES =====================
@app.route("/")
def index():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("Username")
    gender = request.form.get("Gender")
    birthday_str = request.form.get("Birthday")
    phone = request.form.get("phone")
    address = request.form.get("address")
    password = request.form.get("password")

    # Check if username exists
    if User.query.filter_by(username=username).first():
        flash("Username already exists! Please choose another.", "error")
        return redirect(url_for("index"))

    # Parse birthday
    birthday = None
    if birthday_str:
        try:
            birthday = datetime.strptime(birthday_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid birthday format.", "error")
            return redirect(url_for("index"))

    hashed_password = generate_password_hash(password)
    new_user = User(
        username=username,
        gender=gender,
        birthday=birthday,
        phone=phone,
        address=address,
        password=hashed_password
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful!", "success")
        return redirect(url_for("success"))
    except Exception as e:
        db.session.rollback()
        flash("An error occurred during registration. Please try again.", "error")
        return redirect(url_for("index"))

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            flash(f"Welcome, {username}!", "success")
            return redirect(url_for("dashboard"))  # Redirect to a dashboard
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")  # Create this template for post-login

@app.route("/users")
def users():
    all_users = User.query.all()
    return render_template("users.html", users=all_users)  # Still unprotected; add auth later

# ===================== RUN APP =====================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensures the 'user' table exists
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
