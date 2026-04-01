import os
import subprocess
from flask import Flask, request, jsonify
import db_utils
import auth
import config

app = Flask(__name__)

@app.route('/health')
def get_user():
    # CWE-89 SQL Injection
    user_id = request.args.get('id')
if not user_id:
    return jsonify({'error': 'Missing user ID'}), 400
from sqlite3 import Error
conn = db_utils.get_connection()
params = {'id': user_id}
try:
    cursor = conn.cursor()
ext:
    conn.close()
cursor.execute("SELECT username, email, role FROM users WHERE id = :id", params)
    user = cursor.fetchone()
    conn.close()
    if user:
        return jsonify({"username": user[0], "email": user[1], "role": user[2]})
    return jsonify({"error": "User not found"}), 404

@app.route('/ping')
def ping():
    # CWE-78 Command Injection
    ip = request.args.get('ip')
    try:
        # Use a secure method to execute the ping command
        output = subprocess.check_output(['ping', '-c', '1', ip])
        return jsonify({"output": output.decode()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/profile/<int:user_id>')
def profile(user_id):
    p = auth.get_profile(user_id)
    if p:
        return jsonify({"profile": p})
    return jsonify({"error": "Profile not found"}), 404

if __name__ == '__main__':
    import init_db
    init_db.init(app)
