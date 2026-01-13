from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os

app = Flask(__name__)
app.secret_key = 'Repoyo'

# --- DATABASE CONFIGURATION FOR RAILWAY ---
# Railway provides DATABASE_URL for MySQL service (e.g., mysql://user:pass@host:port/db)
# SQLAlchemy requires 'mysql+pymysql://' prefix for MySQL connections
raw_uri = os.environ.get('DATABASE_URL')

if raw_uri:
    if raw_uri.startswith("mysql://"):
        app.config['SQLALCHEMY_DATABASE_URI'] = raw_uri.replace("mysql://", "mysql+pymysql://", 1)
    else:
        # Fallback if it's not MySQL (though Railway MySQL should start with mysql://)
        app.config['SQLALCHEMY_DATABASE_URI'] = raw_uri
else:
    # Local development fallback (ensure MySQL is running locally with this DB)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/registration_db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODEL ---
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), nullable=False, unique=True)  # Added unique constraint for username
    gender = db.Column(db.String(10), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    cellphone_number = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Note: In production, hash passwords with werkzeug.security

# --- ROUTES ---
@app.route('/')
def home():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        from datetime import datetime
        # Basic validation (add more as needed)
        username = request.form.get('Username')
        if not username or len(username) > 16:
            flash("Username must be 1-16 characters.", "error")
            return redirect(url_for('home'))
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose another.", "error")
            return redirect(url_for('home'))
        
        new_user = User(
            username=username,
            gender=request.form.get('Gender'),
            birthdate=datetime.strptime(request.form.get('Birthday'), "%Y-%m-%d").date(),
            cellphone_number=request.form.get('phone'),
            address=request.form.get('address'),
            password=request.form.get('password')  # Hash this in production!
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful!", "success")
        return redirect(url_for('success'))
    except ValueError as e:
        db.session.rollback()
        flash(f"Invalid date format or data: {str(e)}", "error")
        return redirect(url_for('home'))
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('home'))

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/init-db')
def init_db():
    try:
        db.create_all()
        return "<h1>Success!</h1><p>Database tables created. Go back to the home page to register.</p>"
    except Exception as e:
        return f"<h1>Setup Failed</h1><p>Error: {str(e)}</p>"

# --- RAILWAY DEPLOYMENT ---
# Railway sets PORT environment variable; default to 5000 for local dev
port = int(os.environ.get('PORT', 5000))

if __name__ == '__main__':
    # Bind to 0.0.0.0 for Railway; debug=False for production
    app.run(host='0.0.0.0', port=port, debug=False)
