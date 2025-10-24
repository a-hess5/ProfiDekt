import sqlite3
import os
from flask import Flask, request, jsonify, g
from database import (
    init_magiprof_db, init_pokidekt_db,
    get_magiprof_db_connection, get_pokidekt_db_connection
)

app = Flask(__name__)

# Configure paths for both databases
magiprof_db_path = os.path.join(app.instance_path, 'magiprof_database.db')
pokidekt_db_path = os.path.join(app.instance_path, 'pokidekt_database.db')
os.makedirs(app.instance_path, exist_ok=True)

app.config["MAGIPROF_DATABASE"] = magiprof_db_path
app.config["POKIDEKT_DATABASE"] = pokidekt_db_path

# Initialize both databases
with app.app_context():
    init_magiprof_db()
    init_pokidekt_db()


@app.teardown_appcontext
def close_connection(exception):
    """Close both database connections at the end of each request."""
    magiprof_db = getattr(g, '_magiprof_database', None)
    if magiprof_db is not None:
        magiprof_db.close()

    pokidekt_db = getattr(g, '_pokidekt_database', None)
    if pokidekt_db is not None:
        pokidekt_db.close()


# ============================================
# ROOT ROUTE
# ============================================

@app.route('/')
def index():
    return jsonify({
        "message": "Welcome to ProfiDekt Unified API!",
        "databases": {
            "MagiProf": "Card management system",
            "PokiDekt": "Posts management system"
        },
        "endpoints": {
            "magiprof_cards": {
                "GET /api/magiprof/cards": "Get all MagiProf cards",
                "POST /api/magiprof/cards": "Create a new card (requires card_number, name, optional year)"
            },
            "pokidekt_posts": {
                "GET /api/pokidekt/posts": "Get all PokiDekt posts",
                "POST /api/pokidekt/posts": "Create a new post (requires title and content)"
            }
        }
    })


# ============================================
# MAGIPROF API ROUTES - CARDS
# ============================================

@app.route('/api/magiprof/cards', methods=['GET'])
def get_magiprof_cards():
    """Get all cards from the MagiProf database."""
    conn = get_magiprof_db_connection()
    cursor = conn.cursor()

    # Check if the 'cards' table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cards';")
    if cursor.fetchone() is None:
        return jsonify({"error": "The 'cards' table does not exist in the MagiProf database."}), 500

    cards = conn.execute('SELECT * FROM cards').fetchall()
    cards_list = [dict(row) for row in cards]
    return jsonify(cards_list)


@app.route('/api/magiprof/cards', methods=['POST'])
def add_magiprof_card():
    """Add a new card to the MagiProf database."""
    new_card = request.get_json()
    if not new_card or 'card_number' not in new_card or 'name' not in new_card:
        return jsonify({'error': 'Missing card_number or name'}), 400

    card_number = new_card['card_number']
    name = new_card['name']
    year = new_card.get('year', None)  # Optional field

    conn = get_magiprof_db_connection()

    try:
        cursor = conn.cursor()
        if year:
            cursor.execute('INSERT INTO cards (year, card_number, name) VALUES (?, ?, ?)',
                           (year, card_number, name))
        else:
            cursor.execute('INSERT INTO cards (card_number, name) VALUES (?, ?)',
                           (card_number, name))
        new_card_id = cursor.lastrowid
        conn.commit()
    except sqlite3.OperationalError as e:
        return jsonify(
            {'error': f"Database error: {e}. Does the 'cards' table exist in MagiProf database?"}), 500
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    newly_created_card = conn.execute('SELECT * FROM cards WHERE id = ?', (new_card_id,)).fetchone()
    if newly_created_card is None:
        return jsonify({'error': 'Failed to retrieve the created card.'}), 500

    return jsonify(dict(newly_created_card)), 201


# ============================================
# POKIDEKT API ROUTES - POSTS
# ============================================

@app.route('/api/pokidekt/posts', methods=['GET'])
def get_pokidekt_posts():
    """Get all posts from the PokiDekt database."""
    conn = get_pokidekt_db_connection()
    cursor = conn.cursor()

    # Check if the 'posts' table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='posts';")
    if cursor.fetchone() is None:
        return jsonify({"error": "The 'posts' table does not exist in the PokiDekt database."}), 500

    posts = conn.execute('SELECT * FROM posts').fetchall()
    posts_list = [dict(row) for row in posts]
    return jsonify(posts_list)


@app.route('/api/pokidekt/posts', methods=['POST'])
def add_pokidekt_post():
    """Add a new post to the PokiDekt database."""
    new_post = request.get_json()
    if not new_post or 'title' not in new_post or 'content' not in new_post:
        return jsonify({'error': 'Missing title or content'}), 400

    title = new_post['title']
    content = new_post['content']
    conn = get_pokidekt_db_connection()

    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
        new_post_id = cursor.lastrowid
        conn.commit()
    except sqlite3.OperationalError as e:
        return jsonify(
            {'error': f"Database error: {e}. Does the 'posts' table exist in PokiDekt database?"}), 500
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    newly_created_post = conn.execute('SELECT * FROM posts WHERE id = ?', (new_post_id,)).fetchone()
    if newly_created_post is None:
        return jsonify({'error': 'Failed to retrieve the created post.'}), 500

    return jsonify(dict(newly_created_post)), 201


if __name__ == '__main__':
    app.run(debug=True)