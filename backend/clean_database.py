import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from utils.database import get_db_connection

def clean_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Очищаем все данные, кроме пользователей
    tables_to_clean = [
        'order_items',
        'orders',
        'payment_methods',
        'tickets',
        'matches',
        'transfers',
        'news',
        'products'
    ]

    for table in tables_to_clean:
        cursor.execute(f'DELETE FROM {table}')
        print(f'Cleared {table}')

    # Сбрасываем автоинкремент для всех таблиц
    for table in tables_to_clean:
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")

    conn.commit()
    conn.close()
    print('\nDatabase cleaned! Only users remain.')
    print('Run seed_data.py to add fresh data.')

if __name__ == '__main__':
    clean_database()
