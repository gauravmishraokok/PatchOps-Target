from flask import Flask, request, jsonify, redirect
import sqlite3
import subprocess
import pickle
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
    cursor.execute(query, (user_id,))
    users = cursor.fetchall()
    conn.close()
    import json
return jsonify({"users": [dict(row) for row in users]})

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
    import json
obj = json.loads(data)
    return jsonify({"object": str(obj)})

# CWE-639: Insecure Direct Object Reference (IDOR)
@app.route('/profile/<user_id>')
def get_profile(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username, email, ssn FROM users WHERE id = ? AND user_id = ?", (user_id, user_id))
    profile = cursor.fetchone()
    conn.close()
    import json
return jsonify({"profile": dict(profile)})

# CWE-601: Open Redirect
@app.route('/redirect')
def open_redirect():
    redirect_url = request.args.get('url')
    import urllib.parse
parsed_url = urllib.parse.urlparse(redirect_url)
if parsed_url.netloc != 'example.com':
    return jsonify({"error": "Invalid redirect URL"}), 400
return redirect(redirect_url)

# CWE-200: Sensitive Data Exposure
@app.route('/logs')
def get_logs():
    logging.basicConfig(filename='app.log', level=logging.DEBUG)
    logger = logging.getLogger()
    logger.debug(f"User login attempt with IP: {request.remote_addr}")
    logger.debug(f"Database password: {DATABASE_PASSWORD}")
    logger.debug(f"API key: {API_KEY}")
    with open('app.log', 'r') as f:
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
    import hashlib
import os
salt = os.environ.get('SALT')
hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password.hex()))
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
    cursor.execute("DELETE FROM users WHERE id = ? AND user_id = ?", (user_id, user_id))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})

# CWE-434: Unrestricted File Upload
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    filename = file.filename
    import os
if file.filename.endswith(('.txt', '.pdf')) and file.content_length < 1024 * 1024:
    file.save(os.path.join('/tmp', filename))
else:
    return jsonify({"error": "Invalid file type or size"}), 400
    return jsonify({"filename": filename})

# CWE-22: Path Traversal
@app.route('/download')
def download_file():
    filename = request.args.get('file')
    import os
filepath = os.path.normpath(os.path.join('/var/www/files', filename))
if not filepath.startswith('/var/www/files'):
    return jsonify({"error": "Invalid file path"}), 400
    with open(filepath, 'r') as f:
        content = f.read()
    return jsonify({"content": content})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
