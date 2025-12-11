from flask import Blueprint, jsonify, request
import json
from utils.database import get_db_connection
from services.auth_service import verify_token

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders', methods=['POST'])
def create_order():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized'}), 401

    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Invalid token'}), 401

    user_id = payload['user_id']
    data = request.get_json()

    if not data or 'cart' not in data or 'user_data' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    cart = data['cart']
    user_data = data['user_data']

    total_price = sum(item['price'] * item['quantity'] for item in cart)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            'INSERT INTO orders (user_id, total_price, status, user_data) VALUES (?, ?, ?, ?)',
            (user_id, total_price, 'pending', json.dumps(user_data))
        )
        order_id = cursor.lastrowid

        for item in cart:
            item_id = str(item['id'])
            quantity = item['quantity']

            # Проверяем, это билет или товар (билеты имеют ID вида ticket_XXX)
            if item_id.startswith('ticket_'):
                match_id = int(item_id.replace('ticket_', ''))

                # Проверяем доступность билетов на матч
                match = cursor.execute(
                    'SELECT total_tickets, sold_tickets FROM matches WHERE id = ?',
                    (match_id,)
                ).fetchone()

                if match:
                    total_tickets = match['total_tickets'] or 100
                    sold_tickets = match['sold_tickets'] or 0
                    remaining = total_tickets - sold_tickets

                    if quantity > remaining:
                        conn.close()
                        return jsonify({'error': f'Only {remaining} tickets available for this match'}), 400

                    # Увеличиваем счетчик проданных билетов
                    cursor.execute(
                        'UPDATE matches SET sold_tickets = sold_tickets + ? WHERE id = ?',
                        (quantity, match_id)
                    )

                # Сохраняем билет в заказ (используем match_id как product_id)
                cursor.execute(
                    'INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)',
                    (order_id, match_id, quantity, item['price'])
                )
            else:
                # Обычный товар - проверяем наличие и уменьшаем quantity
                product = cursor.execute(
                    'SELECT quantity FROM products WHERE id = ?',
                    (item_id,)
                ).fetchone()

                if product:
                    available_quantity = product['quantity'] or 0

                    if quantity > available_quantity:
                        conn.close()
                        return jsonify({'error': f'Only {available_quantity} units available'}), 400

                    # Уменьшаем количество товара на складе
                    cursor.execute(
                        'UPDATE products SET quantity = quantity - ? WHERE id = ?',
                        (quantity, item_id)
                    )

                cursor.execute(
                    'INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)',
                    (order_id, item_id, quantity, item['price'])
                )

        conn.commit()
        conn.close()

        return jsonify({
            'message': 'Order created successfully',
            'order_id': order_id
        }), 201

    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    order = cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
    conn.close()

    if order:
        return jsonify(dict(order)), 200
    else:
        return jsonify({'error': 'Order not found'}), 404

@orders_bp.route('/orders/user/<int:user_id>', methods=['GET'])
def get_user_orders(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    orders = cursor.execute(
        'SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC',
        (user_id,)
    ).fetchall()
    conn.close()

    return jsonify([dict(order) for order in orders]), 200
