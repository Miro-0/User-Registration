import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# ================= APP SETUP =================
app = Flask(__name__)
app.secret_key = "Repoyo"

# ================= DATABASE (RAILWAY MYSQL ONLY) =================
# Railway provides these environment variables
MYSQL_USER = os.environ["MYSQLUSER"]
MYSQL_PASSWORD = os.environ["MYSQLPASSWORD"]
MYSQL_HOST = os.environ["MYSQLHOST"]
MYSQL_PORT = os.environ["MYSQLPORT"]
MYSQL_DATABASE = os.environ["MYSQLDATABASE"]

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ================= DATABASE MODEL =================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# ================= CREATE TABLES =================
with app.app_context():
    db.create_all()

# ================= ROUTES =================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("Username already exists", "error")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful!", "success")
        return redirect(url_for("home"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials", "error")

    return render_template("login.html")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
