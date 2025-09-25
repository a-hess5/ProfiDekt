import os
from flask import Flask, request, jsonify, g
from database import init_db, get_db_connection

app = Flask(__name__)


db_path = os.path.join(app.instance_path, 'database.db')
os.makedirs(app.instance_path, exist_ok=True)
app.config["DATABASE"] = db_path


with app.app_context():
    init_db()

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return "Welcome! The database is set up and running."

@app.route('/api/posts', methods=['GET'])
def get_posts():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    return jsonify([dict(row) for row in posts])

@app.route('/api/posts', methods=['POST'])
def add_post():
    new_post = request.get_json()
    if not new_post or 'title' not in new_post or 'content' not in new_post:
        return jsonify({'error': 'Missing title or content'}), 400

    title = new_post['title']
    content = new_post['content']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
    new_post_id = cursor.lastrowid
    conn.commit()

    created_post = conn.execute('SELECT * FROM posts WHERE id = ?', (new_post_id,)).fetchone()
    return jsonify(dict(created_post)), 201

if __name__ == '__main__':
    app.run(debug=True)
