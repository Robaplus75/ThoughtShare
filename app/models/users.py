from ..extensions import db
from .blog import Posts, Tags
from sqlalchemy.orm import relationship
from flask_login import UserMixin

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=0)
    posts = relationship('Posts', backref='poster' ,cascade='all, delete-orphan')

