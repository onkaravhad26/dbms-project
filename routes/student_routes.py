from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_db
from werkzeug.security import generate_password_hash, check_password_hash

student_bp = Blueprint('student', __name__)


def student_login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'student_id' not in session:
            flash('Please login to continue.', 'danger')
            return redirect(url_for('student.login'))
        return f(*args, **kwargs)
    return decorated


@student_bp.route('/')
def index():
    return render_template('index.html')


@student_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name        = request.form.get('name', '').strip()
        email       = request.form.get('email', '').strip()
        password    = request.form.get('password', '')
        room_number = request.form.get('room_number', '').strip()
        phone       = request.form.get('phone', '').strip()

        if not name or not email or not password:
            flash('Name, email, and password are required.', 'danger')
            return render_template('register.html')

        hashed_password = generate_password_hash(password)

        try:
            conn = get_db()
            cur  = conn.cursor()
            cur.execute("SELECT id FROM students WHERE email = %s", (email,))
            if cur.fetchone():
                flash('An account with this email already exists.', 'danger')
                cur.close()
                return render_template('register.html')

            cur.execute(
                "INSERT INTO students (name, email, password, room_number, phone) "
                "VALUES (%s, %s, %s, %s, %s)",
                (name, email, hashed_password, room_number, phone)
            )
            conn.commit()
            cur.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('student.login'))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return render_template('register.html')

    return render_template('register.html')


@student_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('login.html')

        try:
            conn = get_db()
            cur  = conn.cursor()
            cur.execute(
                "SELECT id, name, password FROM students WHERE email = %s", (email,)
            )
            student = cur.fetchone()
            cur.close()

            if student and check_password_hash(student[2], password):
                session['student_id']   = student[0]
                session['student_name'] = student[1]
                flash(f'Welcome back, {student[1]}!', 'success')
                return redirect(url_for('student.dashboard'))
            else:
                flash('Invalid email or password.', 'danger')
                return render_template('login.html')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return render_template('login.html')

    return render_template('login.html')


@student_bp.route('/dashboard')
@student_login_required
def dashboard():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute(
            """SELECT c.id, c.title, cat.name, c.status, c.created_at
               FROM complaints c
               LEFT JOIN categories cat ON c.category_id = cat.id
               WHERE c.student_id = %s
               ORDER BY c.created_at DESC""",
            (session['student_id'],)
        )
        complaints = cur.fetchall()
        cur.close()
        return render_template('dashboard.html', complaints=complaints)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return render_template('dashboard.html', complaints=[])


@student_bp.route('/file-complaint', methods=['GET', 'POST'])
@student_login_required
def file_complaint():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("SELECT id, name FROM categories")
        categories = cur.fetchall()

        if request.method == 'POST':
            title       = request.form.get('title', '').strip()
            category_id = request.form.get('category_id', '') or None
            description = request.form.get('description', '').strip()

            if not title or not description:
                flash('Title and description are required.', 'danger')
                cur.close()
                return render_template('file_complaint.html', categories=categories)

            cur.execute(
                "INSERT INTO complaints (student_id, category_id, title, description) "
                "VALUES (%s, %s, %s, %s)",
                (session['student_id'], category_id, title, description)
            )
            conn.commit()
            cur.close()
            flash('Complaint filed successfully!', 'success')
            return redirect(url_for('student.dashboard'))

        cur.close()
        return render_template('file_complaint.html', categories=categories)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('student.dashboard'))


@student_bp.route('/logout')
def logout():
    session.pop('student_id', None)
    session.pop('student_name', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('student.login'))
