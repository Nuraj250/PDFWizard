from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = 'supersecretkey'

    app.config['UPLOAD_FOLDER'] = os.path.join('app', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit

    from .routes import main
    app.register_blueprint(main)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    return app
