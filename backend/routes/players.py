from flask import Blueprint, jsonify
from utils.database import get_db_connection

players_bp = Blueprint('players', __name__)

@players_bp.route('/players', methods=['GET'])
def get_players():
    conn = get_db_connection()
    cursor = conn.cursor()

    players = cursor.execute('SELECT * FROM players').fetchall()
    conn.close()

    return jsonify([dict(player) for player in players]), 200

@players_bp.route('/players/<int:player_id>', methods=['GET'])
def get_player(player_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    player = cursor.execute('SELECT * FROM players WHERE id = ?', (player_id,)).fetchone()
    conn.close()

    if player:
        return jsonify(dict(player)), 200
    else:
        return jsonify({'error': 'Player not found'}), 404
