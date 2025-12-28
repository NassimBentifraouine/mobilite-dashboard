"""
Application Flask pour l'analyse des inégalités de mobilité en France
"""
from flask import Flask
import os

def create_app():
    """Crée et configure l'application Flask"""
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    app.config['DATA_FOLDER'] = os.path.join(os.path.dirname(__file__), 'data')
    app.config['EXPORTS_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports')

    # Créer le dossier exports s'il n'existe pas
    os.makedirs(app.config['EXPORTS_FOLDER'], exist_ok=True)

    # Importer et enregistrer les routes
    from . import routes
    routes.register_routes(app)

    return app
