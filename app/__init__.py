from flask import Flask
from .routes import main_bp
from .routes import user_bp
from .routes import admin_bp



def create_app():
    app = Flask(__name__,template_folder='templates')
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    return app
