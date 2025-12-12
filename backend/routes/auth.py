from flask import Blueprint, request, jsonify
import sqlite3
from utils.database import get_db_connection
from services.auth_service import hash_password, check_password, generate_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Регистрация нового пользователя
    ---
    tags:
      - Аутентификация
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - contact
            - password
          properties:
            contact:
              type: string
              example: user@example.com
            password:
              type: string
              example: password123
            name:
              type: string
              example: Иван Иванов
    responses:
      201:
        description: Пользователь успешно зарегистрирован
      400:
        description: Ошибка валидации или email уже существует
    """
    data = request.get_json()

    if not data or not all(k in data for k in ('contact', 'password')):
        return jsonify({'error': 'Missing required fields'}), 400

    email = data.get('email') or data.get('contact')
    password = data['password']
    name = data.get('name', email)

    hashed_password = hash_password(password)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        role = 'user'  # Все новые пользователи получают роль 'user'
        cursor.execute(
            'INSERT INTO users (email, password, name, role) VALUES (?, ?, ?, ?)',
            (contact, hashed_password, name, role)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        token = generate_token(user_id, contact, role)

        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'id': user_id,
                'name': name,
                'email': contact,
                'role': role
            }
        }), 201

    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Email already exists'}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Вход пользователя в систему
    ---
    tags:
      - Аутентификация
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - contact
            - password
          properties:
            contact:
              type: string
              example: admin@anzhi.ru
            password:
              type: string
              example: admin123
    responses:
      200:
        description: Успешный вход
      401:
        description: Неверный email или пароль
    """
    data = request.get_json()

    if not data or not all(k in data for k in ('contact', 'password')):
        return jsonify({'error': 'Missing email or password'}), 400

    contact = data['contact']
    password = data['password']

    conn = get_db_connection()
    cursor = conn.cursor()

    user = cursor.execute(
        'SELECT * FROM users WHERE email = ?',
        (contact,)
    ).fetchone()

    conn.close()

    if user and check_password(user['password'], password):
        role = dict(user).get('role', 'user')
        token = generate_token(user['id'], user['email'], role)

        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'role': role
            }
        }), 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401
