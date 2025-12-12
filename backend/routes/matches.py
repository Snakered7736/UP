from flask import Blueprint, jsonify, request
from utils.database import get_db_connection
from services.auth_service import verify_admin_token

matches_bp = Blueprint('matches', __name__)

@matches_bp.route('/matches', methods=['GET'])
def get_matches():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Возвращаем только не удалённые матчи
    matches = cursor.execute('SELECT * FROM matches WHERE is_deleted = 0 OR is_deleted IS NULL ORDER BY date DESC').fetchall()
    conn.close()

    return jsonify([dict(match) for match in matches]), 200

@matches_bp.route('/matches/<int:match_id>', methods=['GET'])
def get_match(match_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    match = cursor.execute('SELECT * FROM matches WHERE id = ?', (match_id,)).fetchone()
    conn.close()

    if match:
        return jsonify(dict(match)), 200
    else:
        return jsonify({'error': 'Match not found'}), 404

@matches_bp.route('/matches/upcoming', methods=['GET'])
def get_upcoming_matches():
    """
    Получить последние добавленные матчи
    ---
    tags:
      - Матчи
    responses:
      200:
        description: Список последних матчей
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Возвращаем последние добавленные матчи (по id DESC)
    matches = cursor.execute(
        'SELECT * FROM matches ORDER BY id DESC LIMIT 5'
    ).fetchall()
    conn.close()

    return jsonify([dict(match) for match in matches]), 200

@matches_bp.route('/matches', methods=['POST'])
def create_match():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized'}), 401

    token = auth_header.split(' ')[1]
    payload = verify_admin_token(token)
    if not payload:
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()
    required = ['home_team', 'away_team', 'date', 'time', 'stadium', 'home_team_logo', 'away_team_logo', 'total_tickets']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            'INSERT INTO matches (home_team, away_team, date, time, stadium, score, home_team_logo, away_team_logo, total_tickets, sold_tickets) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (data['home_team'], data['away_team'], data['date'], data['time'], data['stadium'], data.get('score'), data['home_team_logo'], data['away_team_logo'], data['total_tickets'], 0)
        )
        match_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({'message': 'Match created successfully', 'match_id': match_id}), 201

    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@matches_bp.route('/matches/<int:match_id>', methods=['DELETE'])
def delete_match(match_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized'}), 401

    token = auth_header.split(' ')[1]
    payload = verify_admin_token(token)
    if not payload:
        return jsonify({'error': 'Admin access required'}), 403

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Не удаляем матч, а помечаем как удалённый
        cursor.execute('UPDATE matches SET is_deleted = 1 WHERE id = ?', (match_id,))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Match hidden successfully'}), 200

    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500
