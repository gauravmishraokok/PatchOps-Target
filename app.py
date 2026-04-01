from flask import Flask, request, jsonify, session, redirect, url_for
import os
import pickle
import sqlite3
import subprocess

app = Flask(__name__)


app.secret_key = "super_secret_flask_key_12345"

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
