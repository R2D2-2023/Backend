import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, send_from_directory, url_for

import sys
from pathlib import Path
path_root = Path(__file__).parents[0]
sys.path.append(str(path_root))
print(sys.path)

from models import config_db
from routes import config_route


def create_app():
    app = Flask(__name__)
    # if config_filename is not None:
    #     app.config.from_object(config_filename)

   
    # production
    print("Loading config.production.")
    app.config.from_object('azureproject.production')

    db, migrate, csrf = config_db(app)
    config_route(app, csrf, db)
    return app

if os.environ.get("WEBSITE_HOSTNAME") is not None:
    # running on Azure Web App
    app = create_app()
    

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)