# Create Blueprints for different sections of your application

# Import route modules after creating Blueprints to avoid circular imports
from . import main_routes
from .main_routes import main_bp
from .user_routes import user_bp
from .admin_routes import admin_bp
