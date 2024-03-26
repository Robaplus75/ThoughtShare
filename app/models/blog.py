from ..extensions import db
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DATE
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import relationship
import app.models.users

class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    tagged_items = relationship('Tagged_items', backref='tags', cascade='all, delete-orphan')

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(50))
    slug = db.Column(db.String(50), nullable=False, unique=True)
    body = db.Column(db.Text, nullable=False)
    publish = db.Column(DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    tagged_items = relationship('Tagged_items', backref='tagged_posts', cascade='all, delete-orphan')
    comments = relationship("Comment", backref='post', cascade='all, delete-orphan')
    likes = relationship("Like", backref='post', cascade='all, delete-orphan')

class Tagged_items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, ForeignKey("posts.id"))
    tag_id = db.Column(db.Integer, ForeignKey("tags.id"))


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    date_created = db.Column(DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, ForeignKey("users.id"), nullable=False)
    post_id = db.Column(db.Integer, ForeignKey("posts.id"), nullable=False)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, ForeignKey("users.id"), nullable=False)
    post_id = db.Column(db.Integer, ForeignKey("posts.id"), nullable=False)