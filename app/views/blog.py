from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user, login_required
from ..utils import slugify
from werkzeug.utils import secure_filename
from ..models.blog import Posts
from ..extensions import db
from datetime import datetime
from .tags import create_tags, update_tags, get_tags
import os


bp = Blueprint("blog", __name__)

def save_image(file):
    filename = secure_filename(file.filename)
    image_url = current_app.config['UPLOAD_FOLDER'] / filename
    file.save(image_url)
    return filename


@bp.route('/')
def posts():
    posts = Posts.query.all()
    return render_template('index.html', posts=posts)

@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = request.form.get('title')
        slug = slugify(title)
        image = request.files.get("image")
        body = request.form.get("body")
        publish = request.form.get("publish")
        tags = request.form.get("tags")
        user_id = current_user.id

        if not title or not slug or not image or not body or not publish or not tags:
            flash("Please complete the form to Post you thoughts", category="error")
        else:
            publish_date = datetime.strptime(publish, '%Y-%m-%d').date()
            filename = save_image(image)
            post = Posts(title=title, image=filename, slug=slug, body=body, publish=publish_date, user_id=user_id )
            db.session.add(post)
            db.session.commit()
            
            create_tags(tags.split(','), post.id)

            flash("Post created Successfully", category="success")
            return redirect(url_for('blog.detail', slug=slug))

    return render_template("blog/form.html", title="Create Post", post=None)

@bp.route("/detail/<slug>")
def detail(slug):
    post = Posts.query.filter(Posts.slug==slug).first()
    if not post:
        flash("Post Does not exist", category="error")
        return redirect(url_for('blog.posts'))
    else:
        tags = get_tags(post.id)
        return render_template("blog/detail.html", post=post, tags=tags)

@bp.route("/update/<slug>", methods=["GET", "POST"])
@login_required
def update(slug):
    post = Posts.query.filter(Posts.slug==slug).first()
    if not post:
        flash("Post does not exist", category='error')
        return redirect(url_for('blog.posts'))
    getTags = get_tags(post.id)
    if request.method == "POST":
        title = request.form.get('title')
        slug = slugify(title)
        image = request.files.get("image")
        body = request.form.get("body")
        tags = request.form.get("tags")
        publish = request.form.get("publish")

        if not title or not slug or not body or not publish:
            flash("Please complete the form to update your post", category="error")
        else:
            if image:
                filename = save_image(image)
                post.image = filename

            update_tags(tags.split(','), post.id)
            post.title = title
            post.slug = slug
            post.body = body
            post.publish = datetime.strptime(publish, '%Y-%m-%d').date()
            
            db.session.commit()
            flash("Post Updated Successfully", category="success")
            return redirect(url_for('blog.detail', slug=slug))

    return render_template("blog/form.html", post=post, title="Update Post", tags=getTags)

@bp.route("/delete/<slug>")
def delete(slug):
    post = Posts.query.filter(Posts.slug==slug).first()
    if not post:
        flash("Post does not exist", category='error')
    else:
        flash("Post was Deleted", category='danger')
    return redirect(url_for('blog.posts'))