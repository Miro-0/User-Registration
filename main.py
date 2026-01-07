from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(_name_)
app.secret_key = 'Repoyo'

# ================= DATABASE CONFIGURATION =================
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.environ['MYSQLUSER']}:"
    f"{os.environ['MYSQLPASSWORD']}@"
    f"{os.environ['MYSQLHOST']}:"
    f"{os.environ['MYSQLPORT']}/"
    f"{os.environ['MYSQLDATABASE']}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ================= USER MODEL =================
class User(db.Model):
    _tablename_ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    cellphone_number = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(200), nullable=False)

# ================= ROUTES =================
@app.route('/')
def home():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        username = request.form.get('Username')
        gender = request.form.get('Gender')
        birthdate_str = request.form.get('Birthday')
        phone = request.form.get('phone')
        address = request.form.get('address')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('home'))

        birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d").date()

        new_user = User(
            username=username,
            gender=gender,
            birthdate=birthdate,
            cellphone_number=phone,
            address=address,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('success'))

    except Exception as e:
        db.session.rollback()
        flash(f'Database Error: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/users')
def view_users():
    all_users = User.query.all()
    return render_template('users.html', users=all_users)

if _name_ == '_main_':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

