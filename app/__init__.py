from flask import Flask
from os import path, makedirs
from .extensions import db

def create_app():
    app = Flask(__name__)

    UPLOAD_FOLDER = 'uploads'
    if not path.exists(UPLOAD_FOLDER):
        makedirs(UPLOAD_FOLDER)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SECRET_KEY'] = "robel123robel123"
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    db.init_app(app)

    if not path.exists('instance/database.db'):
        create_db(app)
        print("DATABASE CREATED")
    
    from app.views.user import bp as user_bp
    from app.views.user import login_manager
    app.register_blueprint(user_bp)
    login_manager.login_view = 'users.login'
    login_manager.login_message_category = 'error'
    login_manager.init_app(app)

    return app

def create_db(app):
    from .models import Users, Tags, Posts, Tagged_items
    with app.app_context():
        db.create_all()

app = create_app()
