from flask import Blueprint, jsonify, request
from utils.database import get_db_connection
from services.auth_service import verify_token, hash_password

profile_bp = Blueprint('profile', __name__)

# GET /api/profile - получить данные пользователя
@profile_bp.route('/profile', methods=['GET'])
def get_profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized'}), 401

    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Invalid token'}), 401

    user_id = payload['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    user = cursor.execute('SELECT id, name, email, role FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify(dict(user)), 200

# PUT /api/profile - обновить данные пользователя
@profile_bp.route('/profile', methods=['PUT'])
def update_profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized'}), 401

    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Invalid token'}), 401

    user_id = payload['user_id']
    data = request.get_json()

    conn = get_db_connection()
    cursor = conn.cursor()

    # Обновить имя и email
    if 'name' in data:
        cursor.execute('UPDATE users SET name = ? WHERE id = ?', (data['name'], user_id))
    if 'email' in data:
        cursor.execute('UPDATE users SET email = ? WHERE id = ?', (data['email'], user_id))

    # Обновить пароль (если передан)
    if 'password' in data and data['password']:
        hashed = hash_password(data['password'])
        cursor.execute('UPDATE users SET password = ? WHERE id = ?', (hashed, user_id))

    conn.commit()
    conn.close()

    return jsonify({'message': 'Profile updated successfully'}), 200

# GET /api/profile/payment-methods - получить способы оплаты
@profile_bp.route('/profile/payment-methods', methods=['GET'])
def get_payment_methods():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized'}), 401

    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Invalid token'}), 401

    user_id = payload['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    methods = cursor.execute('SELECT * FROM payment_methods WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()

    return jsonify([dict(m) for m in methods]), 200

# POST /api/profile/payment-methods - добавить способ оплаты
@profile_bp.route('/profile/payment-methods', methods=['POST'])
def add_payment_method():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized'}), 401

    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Invalid token'}), 401

    user_id = payload['user_id']
    data = request.get_json()

    required = ['card_number', 'card_holder', 'expiry_date']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        'INSERT INTO payment_methods (user_id, card_number, card_holder, expiry_date, is_default) VALUES (?, ?, ?, ?, ?)',
        (user_id, data['card_number'], data['card_holder'], data['expiry_date'], data.get('is_default', 0))
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'Payment method added'}), 201

# DELETE /api/profile/payment-methods/<id> - удалить способ оплаты
@profile_bp.route('/profile/payment-methods/<int:method_id>', methods=['DELETE'])
def delete_payment_method(method_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized'}), 401

    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Invalid token'}), 401

    user_id = payload['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM payment_methods WHERE id = ? AND user_id = ?', (method_id, user_id))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Payment method deleted'}), 200

# GET /api/profile/orders - получить историю заказов
@profile_bp.route('/profile/orders', methods=['GET'])
def get_orders():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized'}), 401

    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Invalid token'}), 401

    user_id = payload['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Получить заказы пользователя
    orders = cursor.execute('SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC', (user_id,)).fetchall()

    result = []
    for order in orders:
        # Получаем все позиции заказа (товары и билеты)
        # Билеты хранятся как product_id = match_id, товары как обычно
        items = cursor.execute('''
            SELECT
                oi.id,
                oi.order_id,
                oi.product_id,
                oi.quantity,
                oi.price,
                p.name as product_name,
                p.image as product_image
            FROM order_items oi
            LEFT JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        ''', (order['id'],)).fetchall()

        order_items = []
        for item in items:
            item_dict = dict(item)

            # Если нет product_name, значит это билет (product_id = match_id)
            if not item_dict.get('product_name'):
                match = cursor.execute('''
                    SELECT home_team, away_team, date, time
                    FROM matches
                    WHERE id = ?
                ''', (item_dict['product_id'],)).fetchone()

                if match:
                    item_dict['product_name'] = f"Билет: {match['home_team']} - {match['away_team']}"
                    item_dict['product_image'] = 'images/ticket-icon.svg'
                    item_dict['ticket_details'] = f"{match['date']}, {match['time']}"
                else:
                    item_dict['product_name'] = 'Билет (матч не найден)'
                    item_dict['product_image'] = 'images/ticket-icon.svg'

            order_items.append(item_dict)

        result.append({
            'id': order['id'],
            'total': order['total_price'],
            'created_at': order['created_at'],
            'items': order_items
        })

    conn.close()

    return jsonify(result), 200
