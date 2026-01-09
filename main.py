from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'Repoyo'

# ================= DATABASE CONFIGURATION =================
# Try to find the URL in different Railway variables
uri = os.environ.get('DATABASE_URL') or os.environ.get('MYSQL_URL')

# Fix connection string for SQLAlchemy
if uri and uri.startswith("mysql://"):
    uri = uri.replace("mysql://", "mysql+pymysql://", 1)

# Default to local if no cloud DB found (Debugging check)
if not uri:
    print("WARNING: No DATABASE_URL found. Using localhost.")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/registration_db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = uri

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
        return redirect(url_for('success'))

    except Exception as e:
        db.session.rollback()
        # Show the error on the screen so you can see it on your phone
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/users')
def view_users():
    try:
        all_users = User.query.all()
        return render_template('users.html', users=all_users)
    except Exception as e:
        return f"Error loading users: {e}"

# ================= DIAGNOSTIC ROUTE =================
# Visit this route to fix your database
@app.route('/init-db')
def init_db():
    status = []
    
    # 1. Check if we found a database URL
    if uri:
        status.append(f"✅ FOUND DATABASE URL (starts with {uri[:10]}...)")
    else:
        status.append("❌ NO DATABASE URL FOUND! (Did you add the Variable in Railway?)")
        return "<br>".join(status)

    # 2. Try to connect
    try:
        with db.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        status.append("✅ CONNECTION SUCCESSFUL")
    except Exception as e:
        status.append(f"❌ CONNECTION FAILED: {str(e)}")
        return "<br>".join(status)

    # 3. Try to create tables
    try:
        db.create_all()
        status.append("✅ TABLES CREATED SUCCESSFULLY")
    except Exception as e:
        status.append(f"❌ TABLE CREATION FAILED: {str(e)}")
    
    status.append("<br><b>You can now try registering again!</b>")
    return "<br>".join(status)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
