from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os

app = Flask(__name__)
app.secret_key = 'Repoyo'

# --- DATABASE FIX ---
# This looks for Railway's specific database connection string
raw_uri = os.environ.get('DATABASE_URL') or os.environ.get('MYSQL_URL')

if raw_uri:
    # SQLAlchemy requires 'mysql+pymysql://' instead of just 'mysql://'
    if raw_uri.startswith("mysql://"):
        app.config['SQLALCHEMY_DATABASE_URI'] = raw_uri.replace("mysql://", "mysql+pymysql://", 1)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = raw_uri
else:
    # Local fallback
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/registration_db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODEL ---
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    cellphone_number = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(200), nullable=False)

# --- ROUTES ---
@app.route('/')
def home():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        from datetime import datetime
        new_user = User(
            username=request.form.get('Username'),
            gender=request.form.get('Gender'),
            birthdate=datetime.strptime(request.form.get('Birthday'), "%Y-%m-%d").date(),
            cellphone_number=request.form.get('phone'),
            address=request.form.get('address'),
            password=request.form.get('password')
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('success'))
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

if __name__ == '__main__':
    app.run(debug=True)
