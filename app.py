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

@app.route('/api/cards/search', methods=['GET'])
def search_cards():
    """
    Search and filter cards from database.
    Query parameters:
    - q: search query (searches name)
    - view: 'cards', 'all_prints', 'unique'
    - sort: 'name', 'release_date', 'card_number', 'year'
    - order: 'asc' or 'desc'
    - page: page number (default 1)
    - per_page: items per page (default 12)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if cards table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cards';")
    if cursor.fetchone() is None:
        return jsonify({"error": "The 'cards' table does not exist in the database."}), 500

    # Get query parameters
    search_query = request.args.get('q', '').strip()
    view_type = request.args.get('view', 'cards').lower()
    sort_by = request.args.get('sort', 'name').lower()
    order = request.args.get('order', 'asc').lower()
    page = max(1, int(request.args.get('page', 1)))
    per_page = int(request.args.get('per_page', 12))

    # Build base query
    base_query = "SELECT * FROM cards"
    where_clauses = []
    params = []

    # Add search filter
    if search_query:
        where_clauses.append("(name LIKE ? OR card_number LIKE ?)")
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    # Apply view type filter
    if view_type == 'unique':
        # Group by name to get unique cards only
        base_query = "SELECT * FROM cards WHERE id IN (SELECT MIN(id) FROM cards"
        if where_clauses:
            base_query += " WHERE " + " AND ".join(where_clauses)
        base_query += " GROUP BY name)"
        where_clauses = []  # Already included in subquery

    # Combine WHERE clauses
    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)

    # Map sort options to columns
    sort_column_map = {
        'name': 'name',
        'release_date': 'year',
        'card_number': 'card_number',
        'set/number': 'card_number',
        'year': 'year'
    }
    sort_column = sort_column_map.get(sort_by, 'name')

    # Add ORDER BY
    order_direction = 'DESC' if order == 'desc' else 'ASC'
    base_query += f" ORDER BY {sort_column} {order_direction}"

    # Get total count for pagination
    count_query = f"SELECT COUNT(*) FROM ({base_query}) AS subquery"
    cursor.execute(count_query, params)
    total_count = cursor.fetchone()[0]

    # Add pagination
    offset = (page - 1) * per_page
    base_query += f" LIMIT ? OFFSET ?"
    params.extend([per_page, offset])

    # Execute query
    try:
        cards = conn.execute(base_query, params).fetchall()
        cards_list = [dict(row) for row in cards]

        return jsonify({
            'cards': cards_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'total_pages': (total_count + per_page - 1) // per_page
            },
            'filters': {
                'search_query': search_query,
                'view_type': view_type,
                'sort_by': sort_by,
                'order': order
            }
        })
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/cards/stats', methods=['GET'])
def get_cards_stats():
    """Get statistics about the card collection."""
    conn = get_db_connection()

    # Check if cards table exists
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cards';")
    if cursor.fetchone() is None:
        return jsonify({"error": "The 'cards' table does not exist in the database."}), 500

    try:
        total_cards = conn.execute('SELECT COUNT(*) FROM cards').fetchone()[0]
        unique_cards = conn.execute('SELECT COUNT(DISTINCT name) FROM cards').fetchone()[0]

        return jsonify({
            'total_cards': total_cards,
            'unique_cards': unique_cards
        })
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

