from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os
import subprocess

app = Flask(__name__)

SUPER_SECRET_PAYMENT_API_KEY = os.environ.get("SUPER_SECRET_PAYMENT_API_KEY") or "sk_live_9382749823749823748923"

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

@app.route('/user')
def get_user():
    user_id = request.args.get('id', '1')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    query = "SELECT username, email, role FROM users WHERE id = ?"
    try:
        cursor.execute(query, (user_id,))
        users = cursor.fetchall()
        return jsonify({"users": users})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/ping')
def ping_server():
    target_ip = request.args.get('ip', '127.0.0.1')
    command = ["ping", "-c", "1", target_ip]
    try:
        output = subprocess.check_output(command, text=True)
        return jsonify({"output": output})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Ping failed"})

@app.route('/read')
def read_config():
    filename = request.args.get('filename', 'default.cfg')
    base_dir = "configs/"
    file_path = os.path.abspath(os.path.join(base_dir, filename))
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return jsonify({"content": content})
    except FileNotFoundError:
        return jsonify({"error": "File not found"})

@app.route('/greet')
def greet_user():
    name = request.args.get('name', 'Guest')
    return jsonify({"greeting": f"Hello, {name}!"})

if __name__ == '__main__':
    # Ensure DB exists and config folder exists for testing
    if not os.path.exists('configs'):
        os.makedirs('configs')
        with open('configs/default.cfg', 'w') as f:
            f.write("theme=dark\nversion=1.0")

    init_db()
    app.run(port=5000)