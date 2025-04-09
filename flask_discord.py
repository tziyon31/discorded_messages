import requests
import sqlite3
from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta

app = Flask(__name__)
def get_db_connection():
     conn = sqlite3.connect('first_discord_project.db')
     conn.row_factory = sqlite3.Row
     return conn
def init_db():
    with sqlite3.connect('first_discord_project.db') as conn:
        conn.execute(''' 
                        CREATE TABLE IF NOT EXISTS contents(INT PRIMARY KEY,
                       message TEXT, 
                       timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
        ''')
@app.route('/')
def index():
    conn = get_db_connection()
    users = conn.execute("SELECT * FROM contents").fetchall()
    conn.close()
    return render_template('index.html', users=users)

@app.route('//send_message', methods = ['Post'])
def add_message():
    data = request.form
    conn = get_db_connection()
    WEB_HOOK_URL= "https://discord.com/api/webhooks/1356898145568817172/Fwq-OikHNyGKMorSwaqVvaiqfKTgJHNu-yeLbryRkegn_Qo6j_WgBLZgyHHfz5YkKDm8"
    pay_load = {"content" : data["message"]}
    res = requests.post(WEB_HOOK_URL, json = pay_load)
    if 200 <= res.status_code < 300:
        conn.execute("INSERT INTO contents (message, timestamp) VALUES (?,?)", (data["message"],datetime.now()))
        conn.commit()
    conn.close()
    return jsonify({'message': 'message added'}), 201
@app.route("/recent_messages", methods = ["GET"])
def get_messages():
    cutoff_time= datetime.now() - timedelta(minutes = 30)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT message, timestamp FROM contents WHERE  timestamp > ?", (cutoff_time,))
    last_messages = cursor.fetchall()
    conn.close()
    messages = [{"message": row["message"], "timestamp": row["timestamp"]} for row in last_messages]
    return jsonify({"status": 'success', 'message': messages})


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
