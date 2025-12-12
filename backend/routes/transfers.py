from flask import Blueprint, jsonify, request
from utils.database import get_db_connection
from services.auth_service import verify_admin_token
from datetime import datetime

transfers_bp = Blueprint('transfers', __name__)

@transfers_bp.route('/transfers', methods=['GET'])
def get_transfers():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Возвращаем только не удалённые трансферы
    transfers = cursor.execute('SELECT * FROM transfers WHERE is_deleted = 0 OR is_deleted IS NULL ORDER BY date DESC').fetchall()
    conn.close()

    return jsonify([dict(transfer) for transfer in transfers]), 200

@transfers_bp.route('/transfers/<int:transfer_id>', methods=['GET'])
def get_transfer(transfer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    transfer = cursor.execute('SELECT * FROM transfers WHERE id = ?', (transfer_id,)).fetchone()
    conn.close()

    if transfer:
        return jsonify(dict(transfer)), 200
    else:
        return jsonify({'error': 'Transfer not found'}), 404

@transfers_bp.route('/transfers', methods=['POST'])
def create_transfer():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized'}), 401

    token = auth_header.split(' ')[1]
    payload = verify_admin_token(token)
    if not payload:
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()

    required_fields = ['player_name', 'from_club', 'to_club', 'transfer_type']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    player_name = data['player_name']
    from_club = data['from_club']
    to_club = data['to_club']
    transfer_type = data['transfer_type']
    amount = data.get('amount', 0)
    date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    player_photo = data.get('player_photo', 'images/player1.jpg')
    from_club_logo = data.get('from_club_logo', 'images/v1_171.png')
    to_club_logo = data.get('to_club_logo', 'images/v1_170.png')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            'INSERT INTO transfers (player_name, from_club, to_club, transfer_type, amount, date, player_photo, from_club_logo, to_club_logo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (player_name, from_club, to_club, transfer_type, amount, date, player_photo, from_club_logo, to_club_logo)
        )
        transfer_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'message': 'Transfer created successfully',
            'transfer_id': transfer_id
        }), 201

    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@transfers_bp.route('/transfers/<int:transfer_id>', methods=['DELETE'])
def delete_transfer(transfer_id):
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
        # Не удаляем трансфер, а помечаем как удалённый
        cursor.execute('UPDATE transfers SET is_deleted = 1 WHERE id = ?', (transfer_id,))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Transfer hidden successfully'}), 200

    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500
