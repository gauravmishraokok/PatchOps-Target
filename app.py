from flask import Flask, request, jsonify, session, redirect, url_for
import os
import pickle
import sqlite3
import subprocess

app = Flask(__name__)

# VULNERABILITY 1: Hardcoded Secret Key (CWE-798)
app.secret_key = "super_secret_flask_key_12345"

# VULNERABILITY 2: SQL Injection (CWE-89) — PRIMARY TARGET FOR PATCHOPS
@app.route('/user')
def get_user():
    user_id = request.args.get('id')
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    query = f"SELECT username, email, role FROM users WHERE id = {user_id}"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return jsonify({"users": [{"username": r[0], "email": r[1], "role": r[2]} for r in rows]})

# VULNERABILITY 3: Unsafe Deserialization (CWE-502)
@app.route('/import', methods=['POST'])
def import_data():
    data = request.data
    try:
        obj = pickle.loads(data)
        return jsonify({"status": "Imported", "data": str(obj)})
    except Exception as e:
        return jsonify({"error": str(e)})

# VULNERABILITY 4: Command Injection (CWE-78)
@app.route('/dns')
def dns_lookup():
    domain = request.args.get('domain', 'example.com')
    cmd = f"nslookup {domain}"
    result = subprocess.getoutput(cmd)
    return jsonify({"result": result})

# VULNERABILITY 5: Open Redirect (CWE-601)
@app.route('/redirect')
def unsafe_redirect():
    url = request.args.get('next', '/')
    return redirect(url)

# VULNERABILITY 6: Sensitive Data Exposure (CWE-200)
@app.route('/debug/env')
def debug_env():
    return jsonify(dict(os.environ))

# VULNERABILITY 7: Weak Authentication Logic (CWE-287)
users_auth = {
    "admin": "password123",
    "user": "1234"
}

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username in users_auth and users_auth[username] == password:
        session['user'] = username
        return jsonify({"message": "Logged in"})
    return jsonify({"error": "Invalid credentials"}), 401

# VULNERABILITY 8: Missing Authorization Check (CWE-285)
@app.route('/admin')
def admin_panel():
    return jsonify({"secret": "Admin panel data"})

# VULNERABILITY 9: File Upload without Validation (CWE-434)
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    filepath = os.path.join("uploads", file.filename)
    file.save(filepath)
    return jsonify({"message": f"Saved to {filepath}"})

# VULNERABILITY 10: Directory Listing / Info Leak
@app.route('/files')
def list_files():
    files = os.listdir("uploads")
    return jsonify({"files": files})

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER, username TEXT, email TEXT, role TEXT)")
    cursor.execute("INSERT OR IGNORE INTO users VALUES (1, 'alice', 'alice@test.com', 'admin')")
    cursor.execute("INSERT OR IGNORE INTO users VALUES (2, 'bob', 'bob@test.com', 'user')")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    init_db()
    app.run(debug=True, port=5000)
