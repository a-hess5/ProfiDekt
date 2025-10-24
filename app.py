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
        "endpoints": {
            "magiprof_cards": {
                "GET /api/magiprof/cards": "Get all MagiProf cards with pagination and search",
                "GET /api/magiprof/cards/<id>": "Get a specific card by ID"
            }
        }
    })


# ============================================
# MAGIPROF API ROUTES - CARDS
# ============================================

@app.route('/api/magiprof/cards', methods=['GET'])
def get_magiprof_cards():
    """Get all cards from the MagiProf database with pagination and optional search."""
    conn = get_magiprof_db_connection()
    cursor = conn.cursor()

    # Check if the 'cards' table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cards';")
    if cursor.fetchone() is None:
        return jsonify({"error": "The 'cards' table does not exist in the MagiProf database."}), 500

    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    search = request.args.get('search', '', type=str)

    # Validate pagination
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 12

    # Calculate offset
    offset = (page - 1) * per_page

    # Build query based on search
    if search:
        search_term = f"%{search}%"
        count_query = '''
            SELECT COUNT(*) FROM cards 
            WHERE card_name LIKE ? OR alt_name LIKE ? OR flavor_text LIKE ?
        '''
        query = '''
            SELECT * FROM cards 
            WHERE card_name LIKE ? OR alt_name LIKE ? OR flavor_text LIKE ?
            ORDER BY card_name ASC
            LIMIT ? OFFSET ?
        '''
        cursor.execute(count_query, (search_term, search_term, search_term))
        total_cards = cursor.fetchone()[0]
        cursor.execute(query, (search_term, search_term, search_term, per_page, offset))
    else:
        count_query = 'SELECT COUNT(*) FROM cards'
        query = 'SELECT * FROM cards ORDER BY card_name ASC LIMIT ? OFFSET ?'
        cursor.execute(count_query)
        total_cards = cursor.fetchone()[0]
        cursor.execute(query, (per_page, offset))

    total_pages = (total_cards + per_page - 1) // per_page
    cards = cursor.fetchall()
    cards_list = [dict(row) for row in cards]

    return jsonify({
        "cards": cards_list,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total_cards,
            "total_pages": total_pages
        }
    })


@app.route('/api/magiprof/cards/<int:card_id>', methods=['GET'])
def get_magiprof_card_by_id(card_id):
    """Get a specific card by ID from the MagiProf database."""
    conn = get_magiprof_db_connection()
    card = conn.execute('SELECT * FROM cards WHERE id = ?', (card_id,)).fetchone()

    if card is None:
        return jsonify({'error': 'Card not found'}), 404

    return jsonify(dict(card))


@app.route('/api/magiprof/cards/search', methods=['GET'])
def search_magiprof_cards():
    """Advanced search for cards with multiple filters."""
    conn = get_magiprof_db_connection()
    cursor = conn.cursor()

    # Get parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)

    # Search filters
    card_name = request.args.get('card_name', '', type=str)
    rules_text = request.args.get('rules_text', '', type=str)
    card_color = request.args.get('card_color', '', type=str)
    type_line = request.args.get('type_line', '', type=str)
    mana_value = request.args.get('mana_value', '', type=str)
    power = request.args.get('power', '', type=str)
    toughness = request.args.get('toughness', '', type=str)
    flavor_text = request.args.get('flavor_text', '', type=str)
    department = request.args.get('department', '', type=str)

    # Validate pagination
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 12

    # Build WHERE clause dynamically
    where_clauses = []
    params = []

    if card_name:
        where_clauses.append('card_name LIKE ?')
        params.append(f'%{card_name}%')

    if rules_text:
        where_clauses.append(
            '(rules_text1 LIKE ? OR rules_text2 LIKE ? OR rules_text3 LIKE ? OR rules_text4 LIKE ? OR rules_text5 LIKE ?)')
        search_term = f'%{rules_text}%'
        params.extend([search_term, search_term, search_term, search_term, search_term])

    if type_line:
        where_clauses.append(
            '(type1 LIKE ? OR type2 LIKE ? OR type3 LIKE ? OR type4 LIKE ? OR type5 LIKE ? OR type6 LIKE ?)')
        search_term = f'%{type_line}%'
        params.extend([search_term, search_term, search_term, search_term, search_term, search_term])

    if card_color:
        where_clauses.append('card_color LIKE ?')
        params.append(f'%{card_color}%')

    if mana_value:
        where_clauses.append('mana_value LIKE ?')
        params.append(f'%{mana_value}%')

    if power:
        where_clauses.append('power = ?')
        params.append(power)

    if toughness:
        where_clauses.append('toughness = ?')
        params.append(toughness)

    if flavor_text:
        where_clauses.append('flavor_text LIKE ?')
        params.append(f'%{flavor_text}%')

    if department:
        where_clauses.append('department = ?')
        params.append(department)

    # Build final query
    where_clause = ' AND '.join(where_clauses) if where_clauses else '1=1'

    count_query = f'SELECT COUNT(*) FROM cards WHERE {where_clause}'
    query = f'SELECT * FROM cards WHERE {where_clause} ORDER BY card_name ASC LIMIT ? OFFSET ?'

    # Get total count
    cursor.execute(count_query, params)
    total_cards = cursor.fetchone()[0]
    total_pages = (total_cards + per_page - 1) // per_page

    # Get paginated results
    offset = (page - 1) * per_page
    cursor.execute(query, params + [per_page, offset])

    cards = cursor.fetchall()
    cards_list = [dict(row) for row in cards]

    return jsonify({
        "cards": cards_list,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total_cards,
            "total_pages": total_pages
        }
    })


@app.route('/api/magiprof/cards', methods=['POST'])
def add_magiprof_card():
    """Add a new card to the MagiProf database."""
    new_card = request.get_json()
    if not new_card or 'card_name' not in new_card:
        return jsonify({'error': 'Missing required field: card_name'}), 400

    conn = get_magiprof_db_connection()

    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cards (card_year, card_color, card_name, alt_name, mana_value, type1, type2, 
                               type3, type4, type5, type6, rules_text1, rules_text2, rules_text3, 
                               rules_text4, rules_text5, flavor_text, power, toughness, department, 
                               printing, image_filepath)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            new_card.get('card_year'),
            new_card.get('card_color'),
            new_card.get('card_name'),
            new_card.get('alt_name'),
            new_card.get('mana_value'),
            new_card.get('type1'),
            new_card.get('type2'),
            new_card.get('type3'),
            new_card.get('type4'),
            new_card.get('type5'),
            new_card.get('type6'),
            new_card.get('rules_text1'),
            new_card.get('rules_text2'),
            new_card.get('rules_text3'),
            new_card.get('rules_text4'),
            new_card.get('rules_text5'),
            new_card.get('flavor_text'),
            new_card.get('power'),
            new_card.get('toughness'),
            new_card.get('department'),
            new_card.get('printing'),
            new_card.get('image_filepath')
        ))
        new_card_id = cursor.lastrowid
        conn.commit()
    except sqlite3.OperationalError as e:
        return jsonify({'error': f"Database error: {e}"}), 500
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    newly_created_card = conn.execute('SELECT * FROM cards WHERE id = ?', (new_card_id,)).fetchone()
    if newly_created_card is None:
        return jsonify({'error': 'Failed to retrieve the created card.'}), 500

    return jsonify(dict(newly_created_card)), 201


# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True)