from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv("Repoyo")

# ===================== DATABASE CONFIGURATION =====================
# Railway provides DATABASE_URL. We use pymysql as the driver for MySQL.
database_url = os.getenv("MYSQL_URL")

if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    elif database_url.startswith("mysql://"):
        database_url = database_url.replace("mysql://", "mysql+pymysql://", 1)
else:
    # Fallback for local development
    database_url = "sqlite:///site.db"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 280,
    "pool_pre_ping": True,
}

db = SQLAlchemy(app)

# ===================== DATABASE MODEL =====================
class User(db.Model):
    __tablename__ = "users"
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
    return redirect(url_for("register"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        birthday_str = request.form.get("birthday")
        
        # Convert date string to Python date object
        birthday = None
        if birthday_str:
            birthday = datetime.strptime(birthday_str, '%Y-%m-%d').date()

        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "error")
            return redirect(url_for("register"))

        new_user = User(
            username=username,
            gender=request.form.get("gender"),
            birthday=birthday,
            phone=request.form.get("phone"),
            address=request.form.get("address"),
            password=generate_password_hash(password)
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("success"))
        except Exception as e:
            db.session.rollback()
            flash(f"Database Error: {str(e)}", "error")
            return redirect(url_for("register"))

    return render_template("register.html")

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/users")
def users():
    all_users = User.query.all()
    return render_template("users.html", users=all_users)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


