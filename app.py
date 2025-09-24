import sqlite3
import os
from flask import Flask, request, jsonify, g
from database import init_db, get_db_connection

app = Flask(__name__)
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
app.config["DATABASE"] = db_path

# Initialize the database
with app.app_context():
    init_db()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# --- API Routes ---

@app.route('/')
def index():
    return "Welcome! The database is set up and running."


@app.route('/api/posts', methods=['GET'])
def get_posts():
    conn = get_db_connection()
    # Check if the 'posts' table exists before querying
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cards';")
    if cursor.fetchone() is None:
        return jsonify({"error": "The 'posts' table does not exist in the database. Check your schema.sql file."}), 500

    posts = conn.execute('SELECT * FROM posts').fetchall()
    posts_list = [dict(row) for row in posts]
    return jsonify(posts_list)


@app.route('/api/posts', methods=['POST'])
def add_post():
    new_post = request.get_json()
    if not new_post or 'title' not in new_post or 'content' not in new_post:
        return jsonify({'error': 'Missing title or content'}), 400

    title = new_post['title']
    content = new_post['content']
    conn = get_db_connection()

    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
        new_post_id = cursor.lastrowid
        conn.commit()
    except sqlite3.OperationalError as e:
        # table or columns don't exist
        return jsonify(
            {'error': f"Database error: {e}. Does the 'posts' table with 'title' and 'content' columns exist?"}), 500
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    newly_created_post = conn.execute('SELECT * FROM posts WHERE id = ?', (new_post_id,)).fetchone()
    if newly_created_post is None:
        return jsonify({'error': 'Failed to retrieve the created post.'}), 500

    return jsonify(dict(newly_created_post)), 201


if __name__ == '__main__':
    app.run(debug=True)

