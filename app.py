from flask import Flask, request, jsonify, redirect
import sqlite3
import subprocess
import json
import os
import logging

app = Flask(__name__)

# CWE-798: Hardcoded Secrets
import os
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
import os
API_KEY = os.environ.get('API_KEY')
import os
SECRET_TOKEN = os.environ.get('SECRET_TOKEN')

# Database connection
DB_PATH = "users.db"

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

# CWE-89: SQL Injection
@app.route('/user')
def get_user():
    user_id = request.args.get('id')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = "SELECT username, email, role FROM users WHERE id = ?"
    cursor.execute(query)
    users = cursor.fetchall()
    conn.close()
    return jsonify({"users": users})

# CWE-78: Command Injection
@app.route('/ping')
def ping_host():
    target_ip = request.args.get('ip')
    command = ["ping", "-c", "1", target_ip]
    output = subprocess.check_output(command, text=True)
    return jsonify({"result": output})

# CWE-502: Unsafe Deserialization
@app.route('/deserialize')
def deserialize_data():
    data = request.args.get('data')
    obj = json.loads(data)
    return jsonify({"object": str(obj)})

# CWE-639: Insecure Direct Object Reference (IDOR)
@app.route('/profile/<user_id>')
@app.login_required
def get_profile(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username, email, ssn FROM users WHERE id = ? AND owner = ?", (user_id, current_user_id))
    profile = cursor.fetchone()
    conn.close()
    return jsonify({"profile": profile})

# CWE-601: Open Redirect
@app.route('/redirect')
def open_redirect():
    redirect_url = request.args.get('url')
if not redirect_url.startswith(('http://', 'https://')):
    return 'Invalid redirect URL', 400
    return redirect(redirect_url)

# CWE-200: Sensitive Data Exposure
@app.route('/logs')
def get_logs():
    logging.basicConfig(filename='app.log', level=logging.DEBUG)
    logger = logging.getLogger()
    logger.debug(f"User login attempt with IP: {request.remote_addr}")
    
    
    with open('app.log', 'r') as f:
    logs = f.read().replace(DATABASE_PASSWORD, '***').replace(API_KEY, '***')
        logs = f.read()
    return jsonify({"logs": logs})

# CWE-287: Broken Authentication
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    # Plaintext password comparison, no salt/hash
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
user = cursor.fetchone()
if user and hash_password(password, user['salt']) == user['password']:
    user = cursor.fetchone()
    conn.close()
    if user:
        return jsonify({"token": SECRET_TOKEN})
    return jsonify({"error": "Invalid credentials"}), 401

# CWE-862: Missing Authorization
@app.route('/admin/delete_user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    # No authorization check!
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if current_user['role'] == 'admin':
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
else:
    return 'Unauthorized', 401
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})

# CWE-434: Unrestricted File Upload
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
if file and allowed_file(file.filename):
    filename = file.filename
    filename = secure_filename(file.filename)
file.save(os.path.join('/tmp', filename))
    return jsonify({"filename": filename})

# CWE-22: Path Traversal
@app.route('/download')
def download_file():
    filename = request.args.get('file')
if not allowed_file_path(filename):
    filepath = os.path.abspath(os.path.join('/var/www/files', filename))
if not filepath.startswith('/var/www/files/'):
    with open(filepath, 'r') as f:
        content = f.read()
    return jsonify({"content": content})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
