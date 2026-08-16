from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'enquiries.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS enquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        message TEXT,
        created_at TEXT
    )
    ''')
    conn.commit()
    conn.close()

app = Flask(__name__)
CORS(app)

@app.route('/api/submit_enquiry', methods=['POST'])
def submit_enquiry():
    data = request.get_json() or {}
    name = data.get('name','').strip()
    email = data.get('email','').strip()
    phone = data.get('phone','').strip()
    message = data.get('message','').strip()
    if not name or not email or not message:
        return jsonify({'ok': False, 'message': 'name,email,message are required'}), 400

    created_at = datetime.utcnow().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO enquiries (name,email,phone,message,created_at) VALUES (?,?,?,?,?)',
              (name,email,phone,message,created_at))
    eid = c.lastrowid
    conn.commit()
    conn.close()

    return jsonify({'ok': True, 'id': eid, 'created_at': created_at})

@app.route('/api/enquiries', methods=['GET'])
def list_enquiries():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id,name,email,phone,message,created_at FROM enquiries ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()
    items = []
    for r in rows:
        items.append({
            'id': r[0], 'name': r[1], 'email': r[2], 'phone': r[3], 'message': r[4], 'created_at': r[5]
        })
    return jsonify({'ok': True, 'enquiries': items})

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=True)
