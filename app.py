import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from contextlib import contextmanager

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'user-management-secret-key-2024')
DATABASE = 'users.db'

@contextmanager
def get_db():
    """Database connection context manager."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    """Initialize database with users table and sample data."""
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                sex TEXT NOT NULL CHECK (sex IN ('M', 'F')),
                experience INTEGER NOT NULL,
                phone_number TEXT NOT NULL
            )
        ''')
        
        # Add sample data if table is empty
        cursor = conn.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            sample_users = [
                ('purush', 28, 'M', 5, '0101'),
                ('prem', 35, 'M', 12, '0102'),
                ('anil', 42, 'F', 18, '0103'),
                ('raju', 24, 'M', 2, '0104'),
                ('rani', 31, 'F', 8, '0105')
            ]
            conn.executemany(
                'INSERT INTO users (name, age, sex, experience, phone_number) VALUES (?, ?, ?, ?, ?)',
                sample_users
            )

def get_users(age_min=None, age_max=None, exp_min=None, exp_max=None, sex=None):
    """Fetch users with optional filters."""
    with get_db() as conn:
        query = 'SELECT * FROM users WHERE 1=1'
        params = []
        if age_min is not None:
            query += ' AND age >= ?'
            params.append(age_min)
        if age_max is not None:
            query += ' AND age <= ?'
            params.append(age_max)
        if exp_min is not None:
            query += ' AND experience >= ?'
            params.append(exp_min)
        if exp_max is not None:
            query += ' AND experience <= ?'
            params.append(exp_max)
        if sex in ('M', 'F'):
            query += ' AND sex = ?'
            params.append(sex)
        
        query += ' ORDER BY name'
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def get_total_users_count():
    """Get total number of users in the database."""
    with get_db() as conn:
        cursor = conn.execute('SELECT COUNT(*) FROM users')
        return cursor.fetchone()[0]

def add_user(name, age, sex, experience, phone_number):
    """Add a new user to the database."""
    with get_db() as conn:
        conn.execute(
            'INSERT INTO users (name, age, sex, experience, phone_number) VALUES (?, ?, ?, ?, ?)',
            (name, age, sex, experience, phone_number)
        )

@app.route('/')
def index():
    """Display users with optional filters."""
    age_min = request.args.get('age_min', type=int)
    age_max = request.args.get('age_max', type=int)
    exp_min = request.args.get('exp_min', type=int)
    exp_max = request.args.get('exp_max', type=int)
    sex = request.args.get('sex')

    users = get_users(age_min, age_max, exp_min, exp_max, sex)
    total_users = get_total_users_count()
    
    return render_template('index.html', users=users, total_users=total_users)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age', '').strip()
        sex = request.form.get('sex', '').strip()
        experience = request.form.get('experience', '').strip()
        phone_number = request.form.get('phone_number', '').strip()

        errors = []
        if not name:
            errors.append("Name is required.")
        if not age.isdigit() or not (1 <= int(age) <= 120):
            errors.append("Age must be a number between 1 and 120.")
        if sex not in ('M', 'F'):
            errors.append("Sex must be M or F.")
        if not experience.isdigit() or int(experience) < 0:
            errors.append("Experience must be a non-negative number.")
        if not phone_number:
            errors.append("Phone number is required.")

        if errors:
            for err in errors:
                flash(err, 'error')
            return render_template('register.html')

        add_user(name, int(age), sex, int(experience), phone_number)
        flash('User registered successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('register.html')

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)