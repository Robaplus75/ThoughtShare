from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user, login_required
from ..utils import slugify
from werkzeug.utils import secure_filename
from ..models.blog import Posts
from ..extensions import db
from datetime import datetime
import os

bp = Blueprint("blog", __name__)

def save_image(file):
    filename = secure_filename(file.filename)
    image_url = current_app.config['UPLOAD_FOLDER'] / filename
    file.save(image_url)
    return filename


@bp.route('/')
@login_required
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
            flash("Post created Successfully", category="success")
            return redirect(url_for('blog.detail', slug=slug))

    return render_template("blog/form.html", title="Create Post")

@bp.route("/detail/<slug>")
def detail(slug):
    return redirect(url_for("blog.posts"))
    post = Posts.query.filter(Posts.slug==slug).first()
    if not post:
        flash("Post Does not exist", category="error")
        return redirect(url_for('blog.posts'))
    else:
        return render_template("blog/detail.html", post=post)

@bp.route("/update/<slug>", methods=["GET", "POST"])
@login_required
def update(slug):
    post = Posts.query.filter(Posts.slug==slug).first()
    values = {'title':post.title, 'slug':post.slug, 'body':post.body, 'tags':post.tags}
    if not post:
        flash("Post does not exist", category='error')
        return redirect(url_for('blog.posts'))
    if request.method == "POST":
        title = request.form.get('title')
        slug = slugify(title)
        image = request.files.get("image")
        body = request.form.get("body")
        tags = request.form.get("tags")

        if not title or not slug or body or not publish or not tags:
            flash("Please complete the form to update your post", category="error")
        else:
            if image:
                filename = save_image(image)
                post.image = filename
            post.title = title
            post.slug = slug
            post.body = body
            post.tags = tags
            
            db.session.commit()
            flash("Post Updated Successfully", category="success")
            return redirect(f"/{slug}")

    return render_template("blog/form.html", values=values, title="Update Post")

@bp.route("/delete/<slug>")
def delete(slug):
    post = Posts.query.filter(Posts.slug==slug).first()
    if not post:
        flash("Post does not exist", category='error')
    else:
        flash("Post was Deleted", category='danger')
    return redirect(url_for('blog.posts'))