import os
from datetime import date
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- DATABASE CONFIG ---
database_url = os.getenv("MYSQL_URL")
if database_url and database_url.startswith("mysql://"):
    database_url = database_url.replace("mysql://", "mysql+pymysql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODEL ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    gender = db.Column(db.String(20))
    birthday = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    password = db.Column(db.String(120), nullable=False)

# --- CREATE TABLES ---
with app.app_context():
    db.create_all()

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    new_user = User(
        username=request.form.get('username'),
        gender=request.form.get('gender'),
        birthday=request.form.get('birthday'),
        phone=request.form.get('phone'),
        address=request.form.get('address'),
        password=request.form.get('password')
    )

    db.session.add(new_user)
    db.session.commit()
    return render_template('success.html')

@app.route('/users')
def view_users():
    users = User.query.all()

    total_users = len(users)
    male = User.query.filter_by(gender="Male").count()
    female = User.query.filter_by(gender="Female").count()
    other = User.query.filter_by(gender="Other").count()

    # Average age calculation
    ages = []
    for u in users:
        if u.birthday:
            birth_year = int(u.birthday.split("-")[0])
            ages.append(date.today().year - birth_year)

    avg_age = round(sum(ages) / len(ages), 1) if ages else "N/A"

    return render_template(
        'users.html',
        users=users,
        total_users=total_users,
        male=male,
        female=female,
        other=other,
        avg_age=avg_age
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
