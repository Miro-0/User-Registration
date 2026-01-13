import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = "secret_key_here" # Change this to a random string

# Database Configuration
# This uses the Railway environment variable. Ensure you have 'DATABASE_URL' in your Railway variables.
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 1. THE MODEL (Ensuring the table is named 'users')
class User(db.Model):
    __tablename__ = 'users' 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    gender = db.Column(db.String(10))
    birthday = db.Column(db.Date)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(100))
    password = db.Column(db.String(255), nullable=False)

# 2. THE FIX: Create tables automatically if they don't exist
with app.app_context():
    db.create_all()
    print("Database tables checked/created.")

@app.route("/")
def index():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register():
    # Matches the names in the new register.html I gave you
    username = request.form.get("username")
    gender = request.form.get("gender")
    birthday_str = request.form.get("birthday")
    phone = request.form.get("phone")
    address = request.form.get("address")
    password = request.form.get("password")

    # Handle Date conversion
    birthday_obj = None
    if birthday_str:
        try:
            birthday_obj = datetime.strptime(birthday_str, '%Y-%m-%d').date()
        except ValueError:
            birthday_obj = None

    # Check if user exists
    if User.query.filter_by(username=username).first():
        flash("Username already exists!", "error")
        return redirect(url_for("index"))

    # Create new user
    new_user = User(
        username=username,
        gender=gender,
        birthday=birthday_obj,
        phone=phone,
        address=address,
        password=generate_password_hash(password)
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return render_template("success.html")
    except Exception as e:
        db.session.rollback()
        print(f"ERROR: {e}")
        flash("An error occurred during registration.", "error")
        return redirect(url_for("index"))

@app.route("/users")
def users():
    all_users = User.query.all()
    return render_template("users.html", users=all_users)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
