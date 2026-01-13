import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "Repoyo"

# ================= RAILWAY MYSQL =================
DATABASE_URL = os.getenv("MYSQL_URL")

if not DATABASE_URL:
    raise RuntimeError("MYSQL_URL not found. Make sure MySQL service is attached.")

# Fix SQLAlchemy MySQL URL
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ================= MODEL =================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# ================= ROUTES =================
@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            flash("Email already registered")
            return redirect(url_for("register"))

        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        flash("Registered successfully!")
        return redirect(url_for("register"))

    return render_template("register.html")

# ================= START =================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # creates tables automatically in Railway MySQL

    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
