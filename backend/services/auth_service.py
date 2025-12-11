import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

def hash_password(password):
    return generate_password_hash(password)

def check_password(hashed, password):
    return check_password_hash(hashed, password)

def generate_token(user_id, email, role='user'):
    return jwt.encode({'user_id': user_id, 'email': email, 'role': role}, Config.SECRET_KEY, algorithm='HS256')

def verify_token(token):
    try:
        return jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
    except:
        return None

def verify_admin_token(token):
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        if payload.get('role') == 'admin':
            return payload
        return None
    except:
        return None
