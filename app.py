
from flask import Flask, request, jsonify
import sqlite3
import subprocess

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/user')
def get_user():
    user_id = request.args.get('id')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    query = "SELECT username, email, role FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))
    users = cursor.fetchall()
    return jsonify({"users": users})

@app.route('/ping')
def ping_host():
    target_ip = request.args.get('ip')
    import shlex
    command = ['ping', '-c', '1', target_ip]
    output = subprocess.check_output(command, text=True)
    return jsonify({"result": output})

if __name__ == '__main__':
    app.run(port=5000)
