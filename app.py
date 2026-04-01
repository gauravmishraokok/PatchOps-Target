from flask import Flask, request, jsonify, session, redirect, url_for
import os
import pickle
import sqlite3
import subprocess

app = Flask(__name__)

# VULNERABILITY 1: Hardcoded Secret Key (CWE-798)
app.secret_key = "super_secret_flask_key_12345"

# VULNERABILITY 2: Insecure Direct Object Reference (IDOR) (CWE-639)
# No authentication check — anyone can access any profile
@app.route('/profile')
def profile():
    user_id = request.args.get('id')
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT username, email FROM users WHERE id = {user_id}")
    data = cursor.fetchone()
    return jsonify({"profile": data})


# VULNERABILITY 3: Unsafe Deserialization (CWE-502)
# Accepts pickled data from user input
@app.route('/import', methods=['POST'])
def import_data():
    data = request.data
    try:
        obj = pickle.loads(data)  # Arbitrary code execution possible
        return jsonify({"status": "Imported", "data": str(obj)})
    except Exception as e:
        return jsonify({"error": str(e)})


# VULNERABILITY 4: Command Injection (CWE-78)
@app.route('/dns')
def dns_lookup():
    domain = request.args.get('domain', 'example.com')
    cmd = f"nslookup {domain}"
    result = subprocess.getoutput(cmd)  # shell execution
    return jsonify({"result": result})


# VULNERABILITY 5: Open Redirect (CWE-601)
@app.route('/redirect')
def unsafe_redirect():
    url = request.args.get('next', '/')
    return redirect(url)


# VULNERABILITY 6: Sensitive Data Exposure (CWE-200)
# Dumps environment variables
@app.route('/debug/env')
def debug_env():
    return jsonify(dict(os.environ))


# VULNERABILITY 7: Weak Authentication Logic (CWE-287)
users = {
    "admin": "password123",
    "user": "1234"
}

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # No hashing, plaintext comparison
    if username in users and users[username] == password:
        session['user'] = username
        return jsonify({"message": "Logged in"})
    return jsonify({"error": "Invalid credentials"}), 401


# VULNERABILITY 8: Missing Authorization Check
@app.route('/admin')
def admin_panel():
    # Should check role but doesn't
    return jsonify({"secret": "Admin panel data"})


# VULNERABILITY 9: File Upload without Validation (CWE-434)
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    filepath = os.path.join("uploads", file.filename)  # No sanitization
    file.save(filepath)
    return jsonify({"message": f"Saved to {filepath}"})


# VULNERABILITY 10: Directory Listing / Info Leak
@app.route('/files')
def list_files():
    files = os.listdir("uploads")
    return jsonify({"files": files})


def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER, username TEXT, email TEXT)")
    cursor.execute("INSERT INTO users VALUES (1, 'admin', 'admin@test.com')")
    cursor.execute("INSERT INTO users VALUES (2, 'john', 'john@test.com')")
    conn.commit()
    conn.close()


if __name__ == '__main__':
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    init_db()
    app.run(debug=True, port=5001)
