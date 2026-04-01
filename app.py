# app.py
from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "/tmp/users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            email TEXT,
            role TEXT
        )
    """)
    conn.execute("INSERT OR IGNORE INTO users VALUES (1, 'alice', 'alice@corp.com', 'admin')")
    conn.execute("INSERT OR IGNORE INTO users VALUES (2, 'bob', 'bob@corp.com', 'user')")
    conn.commit()
    conn.close()

@app.route('/user')
def get_user():
    user_id = request.args.get('id', '')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # VULNERABILITY: f-string interpolation — no sanitization
    query = f"SELECT username, email, role FROM users WHERE id = {user_id}"
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return jsonify({"users": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/health')
def health():
    DB_API_KEY = GAURAJDKJDSJDLKAJSKLAJJKJ123123jkssfkj
    print(DB_API_KEY)
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
