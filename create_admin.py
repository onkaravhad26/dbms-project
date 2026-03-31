"""
create_admin.py
---------------
Run this ONCE after setting up the database to insert the default admin
account with a properly hashed password.

Usage:
    python create_admin.py

Default credentials inserted:
    Username : admin
    Password : admin123
"""

from werkzeug.security import generate_password_hash
import pymysql

# --- Update these to match your config.py ---
HOST     = 'localhost'
USER     = 'root'
PASSWORD = 'onkar@261206'   # <-- change this
DB       = 'hostel_cms'
# --------------------------------------------

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'   # <-- change if you want

hashed = generate_password_hash(ADMIN_PASSWORD)

try:
    conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, database=DB)
    cur  = conn.cursor()

    # Remove any existing admin with the same username first
    cur.execute("DELETE FROM admins WHERE username = %s", (ADMIN_USERNAME,))

    cur.execute(
        "INSERT INTO admins (username, password) VALUES (%s, %s)",
        (ADMIN_USERNAME, hashed)
    )
    conn.commit()
    cur.close()
    conn.close()
    print(f"[OK] Admin account created successfully.")
    print(f"     Username : {ADMIN_USERNAME}")
    print(f"     Password : {ADMIN_PASSWORD}")
except Exception as e:
    print(f"[ERROR] {e}")
