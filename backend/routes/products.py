from flask import Blueprint, jsonify
from utils.database import get_db_connection

products_bp = Blueprint('products', __name__)

@products_bp.route('/products', methods=['GET'])
def get_products():
    """
    Получить список всех товаров
    ---
    tags:
      - Товары
    responses:
      200:
        description: Список товаров
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    products = cursor.execute('SELECT * FROM products').fetchall()
    conn.close()

    return jsonify([dict(product) for product in products]), 200

@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    product = cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()

    if product:
        return jsonify(dict(product)), 200
    else:
        return jsonify({'error': 'Product not found'}), 404
