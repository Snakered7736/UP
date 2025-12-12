from flask import Blueprint, jsonify, request
from utils.database import get_db_connection
from services.auth_service import verify_admin_token

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/products/<int:product_id>/quantity', methods=['PUT'])
def update_product_quantity(product_id):
    """Обновить количество товара на складе (только админ)"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized'}), 401

    token = auth_header.split(' ')[1]
    payload = verify_admin_token(token)
    if not payload:
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()
    if 'quantity' not in data:
        return jsonify({'error': 'Quantity is required'}), 400

    new_quantity = data['quantity']
    if not isinstance(new_quantity, int) or new_quantity < 0:
        return jsonify({'error': 'Quantity must be a non-negative integer'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('UPDATE products SET quantity = ? WHERE id = ?', (new_quantity, product_id))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Product quantity updated successfully', 'new_quantity': new_quantity}), 200

    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/products', methods=['GET'])
def get_all_products_admin():
    """Получить все товары с количеством (для админа)"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized'}), 401

    token = auth_header.split(' ')[1]
    payload = verify_admin_token(token)
    if not payload:
        return jsonify({'error': 'Admin access required'}), 403

    conn = get_db_connection()
    cursor = conn.cursor()

    products = cursor.execute('SELECT id, name, price, quantity, in_stock FROM products ORDER BY id').fetchall()
    conn.close()

    return jsonify([dict(product) for product in products]), 200
