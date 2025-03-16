from flask import Flask
from flask_cors import CORS
from app.api.routes import api
from config import Config

def create_app():
    app = Flask(__name__,
                template_folder='app/templates',
                static_folder='app/static')
    CORS(app)
    
    # Ensure required directories exist
    Config.create_directories()
    
    # Register blueprints
    app.register_blueprint(api, url_prefix='/api')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=3000)
