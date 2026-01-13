import os
import hashlib
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

# ================= FLASK APP =================
app = Flask(__name__)
app.secret_key = "Repoyo"

# ================= MYSQL (RAILWAY) =================
DATABASE_URL = os.getenv("MYSQL_URL")
if not DATABASE_URL:
    raise RuntimeError("MYSQL_URL not found. Make sure MySQL service is attached.")

# PyMySQL needed format
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ================= MODEL =================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)

# ================= ROUTES =================
@app.route("/", methods=["GET", "POST"])
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            username = request.form.get("Username")
            gender = request.form.get("Gender")
            birthday_str = request.form.get("Birthday")
            phone = request.form.get("phone")
            address = request.form.get("address")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")

            # --- VALIDATION ---
            if password != confirm_password:
                flash("Passwords do not match!", "error")
                return redirect(url_for("register"))

            if len(username) < 8 or len(username) > 16:
                flash("Username must be 8-16 characters", "error")
                return redirect(url_for("register"))

            if User.query.filter_by(username=username).first():
                flash("Username already exists!", "error")
                return redirect(url_for("register"))

            # --- HASH PASSWORD ---
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # --- CONVERT BIRTHDAY TO DATE ---
            try:
                birthday = datetime.strptime(birthday_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid birthday format", "error")
                return redirect(url_for("register"))

            # --- CREATE USER ---
            user = User(
                username=username,
                gender=gender,
                birthday=birthday,
                phone=phone,
                address=address,
                password=hashed_password
            )

            db.session.add(user)
            db.session.commit()

            flash("Registered successfully!", "success")
            return redirect(url_for("register"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "error")
            return redirect(url_for("register"))

    return render_template("register.html")

# ================= ERROR SAFETY =================
@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for("register"))

# ================= START =================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(h
