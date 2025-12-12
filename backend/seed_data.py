import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from utils.database import get_db_connection, init_db
from services.auth_service import hash_password

def seed_database():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Создать тестового администратора
    admin_email = 'admin@anzhi.ru'
    cursor.execute('SELECT id FROM users WHERE email = ?', (admin_email,))
    if not cursor.fetchone():
        admin_password = hash_password('admin123')
        cursor.execute(
            'INSERT INTO users (email, password, name, role) VALUES (?, ?, ?, ?)',
            (admin_email, admin_password, 'Администратор', 'admin')
        )
        conn.commit()
        print('Admin created: admin@anzhi.ru / admin123')

    # Добавляем игроков только если их ещё нет
    cursor.execute('SELECT COUNT(*) as count FROM players')
    if cursor.fetchone()['count'] == 0:
        print('Adding players...')
        players_data = [
        ('Разихан Стенорех', 'Вратарь', 1, 20, 'player1.jpg', 'Надёжный вратарь команды'),
        ('Артём Ван Дейк', 'Защитник', 2, 19, 'player2.jpg', 'Крепкий защитник'),
        ('Николай Скиф', 'Защитник', 3, 19, 'player3.jpg', 'Быстрый защитник'),
        ('Вадим Челсик', 'Полузащитник', 10, 18, 'player4.jpg', 'Капитан команды'),
        ('Дмитрий Ферзев', 'Нападающий', 7, 19, 'player5.jpg', 'Результативный нападающий'),
        ('Шамиль Назиров', 'Тренер', 0, 35, 'player6.jpg', 'Главный тренер'),
        ]

        cursor.executemany(
            'INSERT INTO players (name, position, number, age, photo, bio) VALUES (?, ?, ?, ?, ?, ?)',
            players_data
        )
        print('Players added!')

    # Добавляем товары только если их ещё нет
    cursor.execute('SELECT COUNT(*) as count FROM products')
    if cursor.fetchone()['count'] == 0:
        print('Adding products...')
        products_data = [
            ('Домашняя форма 2025', 4999.0, 'images/forma_dom.jpg', 'M', 1, 'Официальная домашняя форма сезона 2025', 10),
            ('Выездная форма 2025', 4999.0, 'images/forma_away.jpg', 'L', 1, 'Официальная выездная форма', 10),
            ('Шарф болельщика', 1299.0, 'images/scarf.jpg', 'ONE SIZE', 1, 'Шарф с символикой клуба', 10),
            ('Кепка', 999.0, 'images/cap.webp', 'ONE SIZE', 1, 'Бейсболка с логотипом', 10),
            ('Футболка тренировочная', 2499.0, 'images/training_shirt.jpg', 'XL', 1, 'Тренировочная футболка', 10),
            ('Куртка', 7999.0, 'images/jacket.jpg', 'L', 1, 'Зимняя куртка', 10),
        ]

        cursor.executemany(
            'INSERT INTO products (name, price, image, size, in_stock, description, quantity) VALUES (?, ?, ?, ?, ?, ?, ?)',
            products_data
        )
        print('Products added!')

    conn.commit()
    conn.close()
    print('Database seeded successfully!')

if __name__ == '__main__':
    seed_database()
