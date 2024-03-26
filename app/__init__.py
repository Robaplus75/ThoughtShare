""" Project Package  """
from flask import Flask, send_from_directory
from os import path, makedirs
from .extensions import db
from pathlib import Path

def create_app():
    app = Flask(__name__)

    UPLOAD_FOLDER = 'app/uploads'
    if not path.exists(UPLOAD_FOLDER):
        makedirs(UPLOAD_FOLDER)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SECRET_KEY'] = "robel123robel123"
    app.config['UPLOAD_FOLDER'] = Path() / UPLOAD_FOLDER
    db.init_app(app)

    if not path.exists('instance/database.db'):
        create_db(app)
        print("DATABASE CREATED")
    
    from app.views.user import bp as user_bp
    from app.views.blog import bp as blog_bp
    from app.views.user import login_manager

    app.register_blueprint(user_bp)
    app.register_blueprint(blog_bp)

    login_manager.login_view = 'users.login'
    login_manager.login_message_category = 'error'
    login_manager.init_app(app)

    @app.route('/uploads/<filename>')
    def uploads(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'].absolute(), filename)

    return app

def create_admin(name, email, password, app):
    from .models import Users
    from werkzeug.security import generate_password_hash
    with app.app_context():
        hash_password = generate_password_hash(password)
        admin = Users(username=name, email=email, password=hash_password, is_admin=True)
        db.session.add(admin)
        db.session.commit()


def create_db(app):
    from .models import Users, Tags, Posts, Tagged_items, Like, Comment
    with app.app_context():
        db.create_all()
    
    create_admin("admin", "admin@gmail.com", "admin", app)

app = create_app()
