from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    from app.api.routes import api
    app.register_blueprint(api, url_prefix='/api')
    
    return app