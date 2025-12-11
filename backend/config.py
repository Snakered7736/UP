import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, '..', 'database', 'football_club.db')

class Config:
    SECRET_KEY = 'your-secret-key-here-change-in-production'
    DATABASE = DATABASE_PATH
    JSON_AS_ASCII = False
