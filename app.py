import os
from datetime import datetime
from flask import Flask,render_template,request,redirect, url_for, send_from_directory
from flask_login import login_required, current_user, login_user, logout_user
import sys
from pathlib import Path


path_root = Path(__file__).parents[0]
sys.path.append(str(path_root))
print(sys.path)

from models import config_db, config_login
from routes import config_route


def create_app():
    """
    Creates and configures the Flask application instance.

    Returns:
    - Flask: The configured Flask application instance.
    """

    app = Flask(__name__)

    if 'FLASK_TEST' in os.environ:
        app.config.from_object('azureproject.test')
        # WEBSITE_HOSTNAME exists only in production environment
    elif 'WEBSITE_HOSTNAME' not in os.environ:
        # local development, where we'll use environment variables
        print("Loading config.development and environment variables from .env file.")
        app.config.from_object('azureproject.development')
    else:
        # production
        print("Loading config.production.")
        app.config.from_object('azureproject.production')

    db, migrate, crsf = config_db(app)
    config_route(app, crsf, db)
    config_login(app)
    return app


if os.environ.get("WEBSITE_HOSTNAME") is not None:
    # running on Azure Web App
    app = create_app()
    

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
