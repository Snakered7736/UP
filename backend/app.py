from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from config import Config
from utils.database import init_db
from routes import (
    auth_bp, players_bp, news_bp, products_bp,
    matches_bp, tickets_bp, transfers_bp, orders_bp
)
from routes.profile import profile_bp
from routes.admin import admin_bp

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger/"
}

swagger = Swagger(app, config=swagger_config)

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(players_bp, url_prefix='/api')
app.register_blueprint(news_bp, url_prefix='/api')
app.register_blueprint(products_bp, url_prefix='/api')
app.register_blueprint(matches_bp, url_prefix='/api')
app.register_blueprint(tickets_bp, url_prefix='/api')
app.register_blueprint(transfers_bp, url_prefix='/api')
app.register_blueprint(orders_bp, url_prefix='/api')
app.register_blueprint(profile_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')

@app.route('/')
def index():
    return {'message': 'Football Club API', 'version': '1.0'}, 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
