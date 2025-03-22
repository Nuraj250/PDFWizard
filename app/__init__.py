from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = 'supersecretkey'  # Change this in production

    from .routes import main
    app.register_blueprint(main)

    # Ensure uploads folder exists
    os.makedirs('app/uploads', exist_ok=True)

    return app
