from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from ..utils import slugify
from werkzeug.utils import secure_filename
from ..models.blog import Posts
from ..extensions import db
import os

bp = Blueprint("blog", __name__)

def save_image(file):
    filename = secure_filename(file.filename)
    image_url = os.path.join('uploads', filename)
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

        if not title or not slug or not image or body or not publish or not publish or not tags:
            flash("Please complete the form to Post you thoughts", category="error")
        else:
            filename = save_image(image)
            post = Posts(title=title, image=filename, slug=slug, body=body, publish=publish, user_id=user_id )
            db.session.add(post)
            db.session.commit()
            flash("Post created Successfully", category="success")
            return redirect(url_for('blog.detail'))

    return render_template("blog/form.html")

@bp.route("/<slug>")
def title(slug):
    post = Posts.query.filter(Posts.slug==slug).first()
    if not post:
        flash("Post Does not exist", category="error")
        return redirect(url_for(blog.posts))
    else:
        return render_template("blog/detail.html", post=post)
