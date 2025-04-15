from flask import Flask
from config import Config
import utils.url_utils
import utils.text_utils
import services.ai_service
import services.web_service
import services.search_service
from routes.main_routes import init_main_routes
from routes.api_routes import init_api_routes
from routes.admin_routes import init_admin_routes

def create_app():
    """Factory-Funktion, die die Flask-Anwendung erstellt und konfiguriert."""
    app = Flask(__name__)

    # Konfiguration laden
    app.config['DEBUG'] = Config.DEBUG
    app.config['SECRET_KEY'] = Config.SECRET_KEY

    # Routen initialisieren
    init_main_routes(app)
    init_api_routes(app)
    init_admin_routes(app)

    @app.errorhandler(404)
    def page_not_found(e):
        return "404 - Seite nicht gefunden", 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return "500 - Interner Serverfehler", 500

    return app

# App-Instanz erstellen
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT)

# Für WSGI-Server wie Gunicorn oder uWSGI
if __name__ != '__main__':
    app = app
