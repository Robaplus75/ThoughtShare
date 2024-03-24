from ..extensions import db
from .blog import Posts, Tags, Like, Comment
from sqlalchemy.orm import relationship
from flask_login import UserMixin

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=0)
    posts = relationship('Posts', backref='user' ,cascade='all, delete-orphan')
    comments = relationship("Comment", backref='user', cascade='all, delete-orphan')
    likes = relationship("Like", backref='user', cascade='all, delete-orphan')

