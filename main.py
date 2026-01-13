import os
from flask import Flask, render_template, request, redirect
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

# --- THE FIX: THIS RUNS EVERY TIME GUNICORN STARTS ---
with app.app_context():
    db.create_all()

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    # Note: Case sensitive! Matches 'name' in your register.html
    new_user = User(
        username=request.form.get('username'),
        gender=request.form.get('Gender'),   # Changed to capital G
        birthday=request.form.get('Birthday'), # Changed to capital B
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
    return render_template('users.html', users=users)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
