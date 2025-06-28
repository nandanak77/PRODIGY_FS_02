from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Employee

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yoursecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home page
@app.route('/')
def home():
    return render_template('home.html')

# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        if User.query.filter_by(username=username).first():
            flash('⚠️ User already exists', 'warning')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('✅ User created successfully!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('❌ Invalid username or password', 'danger')
    return render_template('login.html')

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('🔒 Logged out successfully', 'info')
    return redirect(url_for('home'))

# Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    employees = Employee.query.all()
    return render_template('dashboard.html', employees=employees)

# Add Employee
@app.route('/add', methods=['POST'])
@login_required
def add():
    name = request.form['name']
    email = request.form['email']
    department = request.form['department']
    if Employee.query.filter_by(email=email).first():
        flash('⚠️ Employee with this email already exists', 'warning')
    else:
        employee = Employee(name=name, email=email, department=department)
        db.session.add(employee)
        db.session.commit()
        flash('✅ Employee added', 'success')
    return redirect(url_for('dashboard'))

# Delete Employee
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    emp = Employee.query.get_or_404(id)
    db.session.delete(emp)
    db.session.commit()
    flash('🗑️ Employee deleted', 'info')
    return redirect(url_for('dashboard'))

# Update Employee
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    emp = Employee.query.get_or_404(id)
    if request.method == 'POST':
        emp.name = request.form['name']
        emp.email = request.form['email']
        emp.department = request.form['department']
        db.session.commit()
        flash('✏️ Employee updated', 'success')
        return redirect(url_for('dashboard'))
    return render_template('update.html', emp=emp)

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
