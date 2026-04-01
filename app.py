from flask import Flask, request, jsonify
import sqlite3

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

if __name__ == '__main__':
    app.run(port=5000)