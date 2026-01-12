import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'Repoyo'

# --- RAILWAY / DATABASE CONFIG ---
# Try Railway MySQL connection vars
db_user = os.environ.get("MYSQLUSER")
db_pass = os.environ.get("MYSQLPASSWORD")
db_host = os.environ.get("MYSQLHOST")
db_port = os.environ.get("MYSQLPORT")
db_name = os.environ.get("MYSQLDATABASE")

if db_user and db_pass and db_host and db_port and db_name:
    # Build SQLAlchemy DB URI
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{db_user}:{db_pass}"
        f"@{db_host}:{db_port}/{db_name}"
    )
else:
    # Fall back to local development database
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "mysql+pymysql://root:@localhost/registration_db"
    )

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
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

