from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os
import subprocess

app = Flask(__name__)

# VULNERABILITY 1: Hardcoded Secret (CWE-798)
# An AI should identify this and move it to os.environ.get()
SUPER_SECRET_PAYMENT_API_KEY = "sk_live_9382749823749823748923"

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER, username TEXT, email TEXT, role TEXT)''')
    cursor.execute("INSERT INTO users VALUES (1, 'alice', 'alice@admin.com', 'admin')")
    cursor.execute("INSERT INTO users VALUES (2, 'bob', 'bob@user.com', 'user')")
    conn.commit()
    conn.close()

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

# VULNERABILITY 2: SQL Injection (CWE-89)
# The classic flaw. Unsanitized input directly into an f-string.
@app.route('/user')
def get_user():
    user_id = request.args.get('id', '1')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    query = f"SELECT username, email, role FROM users WHERE id = {user_id}"
    try:
        cursor.execute(query)
        users = cursor.fetchall()
        return jsonify({"users": users})
    except Exception as e:
        return jsonify({"error": str(e)})

# VULNERABILITY 3: Command Injection (CWE-78)
# Takes a target IP and pings it, but doesn't sanitize the input.
# Attacker can send: ?ip=8.8.8.8; cat /etc/passwd
@app.route('/ping')
def ping_server():
    target_ip = request.args.get('ip', '127.0.0.1')
    # Unsafe subprocess call using shell=True
    command = f"ping -c 1 {target_ip}"
    try:
        output = subprocess.check_output(command, shell=True, text=True)
        return jsonify({"output": output})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Ping failed"})

# VULNERABILITY 4: Local File Inclusion / Path Traversal (CWE-22)
# Allows reading local files. Doesn't sanitize for '../'
# Attacker can send: ?filename=../../../../etc/passwd
@app.route('/read')
def read_config():
    filename = request.args.get('filename', 'default.cfg')
    base_dir = "configs/"
    
    # Unsafe path concatenation
    file_path = base_dir + filename
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return jsonify({"content": content})
    except FileNotFoundError:
        return jsonify({"error": "File not found"})

# VULNERABILITY 5: Reflected Cross-Site Scripting (XSS) (CWE-79)
# Directly rendering user input into HTML without escaping it.
# Attacker can send: ?name=<script>alert('XSS')</script>
@app.route('/greet')
def greet_user():
    name = request.args.get('name', 'Guest')
    # Unsafe template rendering
    html_template = f"<h1>Hello, {name}!</h1><p>Welcome to our platform.</p>"
    return render_template_string(html_template)

if __name__ == '__main__':
    # Ensure DB exists and config folder exists for testing
    if not os.path.exists('configs'):
        os.makedirs('configs')
        with open('configs/default.cfg', 'w') as f:
            f.write("theme=dark\nversion=1.0")
    
    init_db()
    app.run(port=5000)
