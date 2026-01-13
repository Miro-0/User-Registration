import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "secret_key_for_session" # Required for flash messages

# --- DATABASE CONFIGURATION ---
# Railway provides 'MYSQL_URL'. We convert it to work with SQLAlchemy & PyMySQL.
database_url = os.getenv("MYSQL_URL")
if database_url and database_url.startswith("mysql://"):
    database_url = database_url.replace("mysql://", "mysql+pymysql://", 1)

# Fallback to SQLite for local testing if MySQL_URL is not found
app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///local.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- USER MODEL ---
# Fields are named to match exactly what your users.html template expects
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    gender = db.Column(db.String(20))
    birthdate = db.Column(db.String(50))      # Changed from 'birthday' to match users.html
    cellphone_number = db.Column(db.String(20)) # Changed from 'phone' to match users.html
    address = db.Column(db.String(200))
    password = db.Column(db.String(120), nullable=False)

# Create tables automatically on startup
with app.app_context():
    db.create_all()

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        # DATA FETCHING: Note the capitalized keys to match register.html
        # request.form.get('Username') matches <input name="Username">
        username = request.form.get('Username')
        gender = request.form.get('Gender')
        birthday = request.form.get('Birthday')
        phone = request.form.get('phone')
        address = request.form.get('address')
        password = request.form.get('password')

        # SAVING TO DATABASE
        new_user = User(
            username=username,
            gender=gender,
            birthdate=birthday,
            cellphone_number=phone,
            address=address,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()
        
        # Redirect to your success.html after saving
        return render_template('success.html')
        
    except Exception as e:
        flash(f"Error saving to database: {e}", "error")
        return redirect(url_for('index'))

@app.route('/users')
def view_users():
    # Fetch all users from MySQL to display in users.html
    users = User.query.all()
    return render_template('users.html', users=users)

if __name__ == '__main__':
    # Standard Flask port for Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
