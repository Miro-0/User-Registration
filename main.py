from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "Repoyo"  # Change to a strong secret in production

# ===================== DATABASE CONFIG =====================
# Railway provides DATABASE_URL like:
# mysql+pymysql://<user>:<password>@<host>:<port>/<database>
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable not set!")

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ===================== DATABASE MODEL =====================
class User(db.Model):
    __tablename__ = "user"
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
    username = request.form.get("username")
    gender = request.form.get("gender")
    birthday_str = request.form.get("birthday")
    birthday = datetime.strptime(birthday_str, "%Y-%m-%d").date() if birthday_str else None
    phone = request.form.get("phone")
    address = request.form.get("address")
    password = request.form.get("password")

    if User.query.filter_by(username=username).first():
        return "Username already exists! Please choose another.", 400

    hashed_password = generate_password_hash(password)
    new_user = User(
        username=username,
        gender=gender,
        birthday=birthday,
        phone=phone,
        address=address,
        password=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()

    return render_template("success.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            return f"Welcome, {username}!"
        else:
            return "Invalid username or password", 401
    return render_template("login.html")

@app.route("/users")
def users():
    all_users = User.query.all()
    return render_template("users.html", users=all_users)

# ===================== RUN APP =====================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure table exists
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
