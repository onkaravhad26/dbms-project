from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_db
from werkzeug.security import generate_password_hash, check_password_hash

admin_bp = Blueprint('admin', __name__)


def admin_login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Admin access required. Please login.', 'danger')
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username and password are required.', 'danger')
            return render_template('admin/admin_login.html')

        try:
            conn = get_db()
            cur  = conn.cursor()
            cur.execute(
                "SELECT id, username, password FROM admins WHERE username = %s",
                (username,)
            )
            admin = cur.fetchone()
            cur.close()

            if admin and check_password_hash(admin[2], password):
                session['admin_id']   = admin[0]
                session['admin_name'] = admin[1]
                flash(f'Welcome, {admin[1]}!', 'success')
                return redirect(url_for('admin.admin_dashboard'))
            else:
                flash('Invalid username or password.', 'danger')
                return render_template('admin/admin_login.html')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return render_template('admin/admin_login.html')

    return render_template('admin/admin_login.html')


@admin_bp.route('/dashboard')
@admin_login_required
def admin_dashboard():
    try:
        conn = get_db()
        cur  = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Pending'")
        pending = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM complaints WHERE status = 'In Progress'")
        in_progress = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Resolved'")
        resolved = cur.fetchone()[0]

        cur.close()
        return render_template('admin/admin_dashboard.html',
                               pending=pending,
                               in_progress=in_progress,
                               resolved=resolved)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return render_template('admin/admin_dashboard.html',
                               pending=0, in_progress=0, resolved=0)


@admin_bp.route('/complaints')
@admin_login_required
def view_complaints():
    status_filter = request.args.get('status', 'All')
    try:
        conn = get_db()
        cur  = conn.cursor()

        if status_filter == 'All' or not status_filter:
            cur.execute(
                """SELECT c.id, s.name, s.room_number, cat.name,
                          c.title, c.status, c.created_at
                   FROM complaints c
                   JOIN students s ON c.student_id = s.id
                   LEFT JOIN categories cat ON c.category_id = cat.id
                   ORDER BY c.created_at DESC"""
            )
        else:
            cur.execute(
                """SELECT c.id, s.name, s.room_number, cat.name,
                          c.title, c.status, c.created_at
                   FROM complaints c
                   JOIN students s ON c.student_id = s.id
                   LEFT JOIN categories cat ON c.category_id = cat.id
                   WHERE c.status = %s
                   ORDER BY c.created_at DESC""",
                (status_filter,)
            )
        complaints = cur.fetchall()
        cur.close()
        return render_template('admin/view_complaints.html',
                               complaints=complaints,
                               status_filter=status_filter)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return render_template('admin/view_complaints.html',
                               complaints=[], status_filter='All')


@admin_bp.route('/update-status/<int:complaint_id>', methods=['GET', 'POST'])
@admin_login_required
def update_status(complaint_id):
    try:
        conn = get_db()
        cur  = conn.cursor()

        if request.method == 'POST':
            new_status = request.form.get('status', '')
            remark     = request.form.get('remark', '').strip()

            if not new_status:
                flash('Please select a status.', 'danger')
                cur.close()
                return redirect(url_for('admin.update_status',
                                        complaint_id=complaint_id))

            cur.execute(
                "UPDATE complaints SET status = %s, admin_remark = %s "
                "WHERE id = %s",
                (new_status, remark, complaint_id)
            )
            conn.commit()
            cur.close()
            flash('Complaint status updated successfully!', 'success')
            return redirect(url_for('admin.view_complaints'))

        cur.execute(
            """SELECT c.id, c.title, c.description, c.status, c.admin_remark,
                      s.name, s.room_number, cat.name, c.created_at
               FROM complaints c
               JOIN students s ON c.student_id = s.id
               LEFT JOIN categories cat ON c.category_id = cat.id
               WHERE c.id = %s""",
            (complaint_id,)
        )
        complaint = cur.fetchone()
        cur.close()

        if not complaint:
            flash('Complaint not found.', 'danger')
            return redirect(url_for('admin.view_complaints'))

        return render_template('admin/update_status.html', complaint=complaint)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('admin.view_complaints'))


@admin_bp.route('/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    flash('Admin logged out successfully.', 'success')
    return redirect(url_for('admin.admin_login'))
