import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "Repoyo"

# ================= MYSQL (RAILWAY) =================
DATABASE_URL = os.getenv("MYSQL_URL")

if not DATABASE_URL:
    raise RuntimeError("MYSQL_URL not found. Make sure MySQL service is attached.")

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
@app.route("/register", methods=["GET", "POST"])  # 🔥 ADDED FIX
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(email=email).first():
            flash("Email already registered")
            return redirect(url_for("register"))

        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        flash("Registered successfully!")
        return redirect(url_for("register"))  # always valid now

    return render_template("register.html")

# ================= ERROR SAFETY =================
@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for("register"))  # 🔥 PREVENTS NOT FOUND

# ================= START =================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
