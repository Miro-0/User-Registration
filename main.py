from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os 
from werkzeug.security import generate_password_hash  

app = Flask(__name__)

# Secret key for flash messages
app.secret_key = 'Repoyo'  # ⚠ Consider moving this to an env var for security in production

# ================= DATABASE CONFIGURATION =================
# Use Railway's DATABASE_URL env var (includes host, port, user, password, etc.)
# Fallback to local MySQL for testing
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/registration_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ================= USER MODEL =================
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    cellphone_number = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.address}>'

# ================= ROUTES =================
@app.route('/')
def home():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        # Get form data
        username = request.form.get('Username')
        gender = request.form.get('Gender')
        birthdate_str = request.form.get('Birthday')
        phone = request.form.get('phone')
        address = request.form.get('address')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Password validation
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('home'))

        # Convert birthdate string to date object
        birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d").date()

        # Hash the password for security
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Create new user
        new_user = User(
            username=username,
            gender=gender,
            birthdate=birthdate,
            cellphone_number=phone,
            address=address,
            password=hashed_password  # Store hashed password
        )

        # Save to database
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates tables if they don't exist
    app.run(debug=True)

