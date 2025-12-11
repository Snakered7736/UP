from flask import Blueprint, jsonify, request
from utils.database import get_db_connection
from services.auth_service import verify_admin_token
from datetime import datetime

news_bp = Blueprint('news', __name__)

@news_bp.route('/news', methods=['GET'])
def get_news():
    conn = get_db_connection()
    cursor = conn.cursor()

    news = cursor.execute('SELECT * FROM news ORDER BY date DESC').fetchall()
    conn.close()

    return jsonify([dict(article) for article in news]), 200

@news_bp.route('/news/<int:news_id>', methods=['GET'])
def get_news_item(news_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    article = cursor.execute('SELECT * FROM news WHERE id = ?', (news_id,)).fetchone()
    conn.close()

    if article:
        return jsonify(dict(article)), 200
    else:
        return jsonify({'error': 'News not found'}), 404

@news_bp.route('/news', methods=['POST'])
def create_news():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized'}), 401

    token = auth_header.split(' ')[1]
    payload = verify_admin_token(token)
    if not payload:
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()

    if not data or 'title' not in data or 'content' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    title = data['title']
    content = data['content']
    image = data.get('image', 'images/v1_182.png')
    date = datetime.now().strftime('%Y-%m-%d')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            'INSERT INTO news (title, content, image, date) VALUES (?, ?, ?, ?)',
            (title, content, image, date)
        )
        news_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'message': 'News created successfully',
            'news_id': news_id
        }), 201

    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500
