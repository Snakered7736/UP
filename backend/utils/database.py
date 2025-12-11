import sqlite3
from config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Миграция: добавить поле role, если его нет
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'role' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
        conn.commit()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            number INTEGER NOT NULL,
            age INTEGER NOT NULL,
            photo TEXT,
            bio TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            image TEXT,
            date TEXT NOT NULL,
            category TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            image TEXT,
            size TEXT NOT NULL,
            in_stock BOOLEAN NOT NULL DEFAULT 1,
            description TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            sector TEXT NOT NULL,
            row INTEGER NOT NULL,
            seat INTEGER NOT NULL,
            price REAL NOT NULL,
            available BOOLEAN NOT NULL DEFAULT 1,
            FOREIGN KEY (match_id) REFERENCES matches (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            stadium TEXT NOT NULL,
            score TEXT
        )
    ''')

    # Миграция: добавить поля home_team_logo и away_team_logo, если их нет
    cursor.execute("PRAGMA table_info(matches)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'home_team_logo' not in columns:
        cursor.execute("ALTER TABLE matches ADD COLUMN home_team_logo TEXT DEFAULT 'images/v1_171.png'")
        conn.commit()
    if 'away_team_logo' not in columns:
        cursor.execute("ALTER TABLE matches ADD COLUMN away_team_logo TEXT DEFAULT 'images/v1_170.png'")
        conn.commit()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transfers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            from_club TEXT,
            to_club TEXT NOT NULL,
            transfer_type TEXT NOT NULL,
            date TEXT NOT NULL,
            amount TEXT
        )
    ''')

    # Миграция: добавить поля для картинок трансферов
    cursor.execute("PRAGMA table_info(transfers)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'player_photo' not in columns:
        cursor.execute("ALTER TABLE transfers ADD COLUMN player_photo TEXT DEFAULT 'images/player1.jpg'")
        conn.commit()
    if 'from_club_logo' not in columns:
        cursor.execute("ALTER TABLE transfers ADD COLUMN from_club_logo TEXT DEFAULT 'images/v1_171.png'")
        conn.commit()
    if 'to_club_logo' not in columns:
        cursor.execute("ALTER TABLE transfers ADD COLUMN to_club_logo TEXT DEFAULT 'images/v1_170.png'")
        conn.commit()

    # Миграция: добавить поле quantity для товаров
    cursor.execute("PRAGMA table_info(products)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'quantity' not in columns:
        cursor.execute("ALTER TABLE products ADD COLUMN quantity INTEGER DEFAULT 10")
        conn.commit()

    # Миграция: добавить поле total_tickets для матчей
    cursor.execute("PRAGMA table_info(matches)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'total_tickets' not in columns:
        cursor.execute("ALTER TABLE matches ADD COLUMN total_tickets INTEGER DEFAULT 100")
        conn.commit()
    if 'sold_tickets' not in columns:
        cursor.execute("ALTER TABLE matches ADD COLUMN sold_tickets INTEGER DEFAULT 0")
        conn.commit()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            ticket_id INTEGER,
            total_price REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            user_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (ticket_id) REFERENCES tickets (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payment_methods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            card_number TEXT NOT NULL,
            card_holder TEXT NOT NULL,
            expiry_date TEXT NOT NULL,
            is_default BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()
