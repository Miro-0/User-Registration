import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- DATABASE CONFIGURATION ---
# Railway provides 'MYSQL_URL'. We convert it to work with SQLAlchemy & PyMySQL.
database_url = os.getenv("MYSQL_URL")
if database_url and database_url.startswith("mysql://"):
    database_url = database_url.replace("mysql://", "mysql+pymysql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///local.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- USER MODEL ---
# This matches the fields in your register.html and users.html
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    gender = db.Column(db.String(20))
    birthday = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    password = db.Column(db.String(120), nullable=False)

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    # 1. Get data from the form (matching 'name' attributes in your HTML)
    new_user = User(
        username=request.form.get('username'),
        gender=request.form.get('Gender'),
        birthday=request.form.get('Birthday'),
        phone=request.form.get('phone'),
        address=request.form.get('address'),
        password=request.form.get('password') # In a real app, hash this!
    )

    # 2. Save to MySQL
    try:
        db.session.add(new_user)
        db.session.commit()
        # 3. Redirect to your success page
        return render_template('success.html')
    except Exception as e:
        return f"There was an issue saving to the database: {e}"

@app.route('/users')
def view_users():
    users = User.query.all()
    return render_template('users.html', users=users)

if __name__ == '__main__':
    # Create tables automatically if they don't exist
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8080)
