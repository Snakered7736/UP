from flask import Blueprint, jsonify, request
from utils.database import get_db_connection

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('/tickets', methods=['GET'])
def get_tickets():
    match_id = request.args.get('match_id')

    conn = get_db_connection()
    cursor = conn.cursor()

    if match_id:
        tickets = cursor.execute(
            'SELECT * FROM tickets WHERE match_id = ? AND available = 1',
            (match_id,)
        ).fetchall()
    else:
        tickets = cursor.execute('SELECT * FROM tickets WHERE available = 1').fetchall()

    conn.close()

    return jsonify([dict(ticket) for ticket in tickets]), 200

@tickets_bp.route('/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    ticket = cursor.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,)).fetchone()
    conn.close()

    if ticket:
        return jsonify(dict(ticket)), 200
    else:
        return jsonify({'error': 'Ticket not found'}), 404
