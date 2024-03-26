from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import current_user, login_required
from ..utils import slugify, pagination
from werkzeug.utils import secure_filename
from ..models.blog import Posts, Comment, Like
from ..extensions import db
from datetime import datetime
from .tags import create_tags, update_tags, get_tags
from sqlalchemy import or_
import os


bp = Blueprint("blog", __name__)

def save_image(file):
    filename = secure_filename(file.filename)
    image_url = current_app.config['UPLOAD_FOLDER'] / filename
    file.save(image_url)
    return filename

@bp.route('/landing-page')
def landing_page():
    return render_template("landing_page.html")

@bp.route('/')
def posts():
    keywords = request.args.get('q')
    if keywords:
        return redirect(url_for('blog.search_posts', keywords=keywords))
    posts = Posts.query.all()
    page = request.args.get('page') or 1
    count = len(posts)
    paginate = pagination(count, int(page), 3)
    print(paginate['prev_page'])
    posts = posts[paginate['offset']:(paginate['offset'] + paginate['per_page'])]

    return render_template('index.html', posts=posts, paginate=paginate, keywords=None, now=datetime.now().date(), user=current_user)

@bp.route('/search/<keywords>')
def search_posts(keywords):
    q = keywords
    page = request.args.get('page') or 1
    posts = Posts.query.filter(or_(Posts.title.like(f"%{q}%"), Posts.body.like(f"%{q}%"))).all()
    paginate = pagination(len(posts), int(page), 3)
    posts = posts[paginate['offset']:(paginate['offset'] + paginate['per_page'])]
    
    return render_template('index.html', posts=posts, paginate=paginate, keywords=keywords, now=datetime.now().date(), user=current_user)


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = request.form.get('title')
        slug = slugify(title)
        image = request.files.get("image")
        body = request.form.get("body")
        tags = request.form.get("tags")
        user_id = current_user.id

        if not title or not slug or not body or not tags:
            flash("Please complete the form to Post you thoughts", category="error")
        else:
            if image:
                filename = save_image(image)
                post = Posts(title=title, image=filename, slug=slug, body=body, user_id=user_id )
            else:
                post = Posts(title=title, slug=slug, body=body, user_id=user_id )
            db.session.add(post)
            db.session.commit()
            
            create_tags(tags.split(','), post.id)

            flash("Post created Successfully", category="success")
            return redirect(url_for('blog.detail', slug=slug))

    return render_template("blog/form.html", title="Create Post", post=None, user=current_user)

@bp.route("/detail/<slug>")
def detail(slug):
    post = Posts.query.filter(Posts.slug==slug).first()
    if not post:
        flash("Post Does not exist", category="error")
        return redirect(url_for('blog.posts'))
    else:
        tags = get_tags(post.id)
        return render_template("blog/detail.html", post=post, tags=tags, user=current_user)

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

        if not title or not slug or not body:
            flash("Please complete the form to update your post", category="error")
        else:
            if image:
                filename = save_image(image)
                post.image = filename

            update_tags(tags.split(','), post.id)
            post.title = title
            post.slug = slug
            post.body = body
            
            db.session.commit()
            flash("Post Updated Successfully", category="success")
            return redirect(url_for('blog.detail', slug=slug))

    return render_template("blog/form.html", post=post, title="Update Post", tags=getTags, user=current_user)


@bp.route("/delete/<slug>")
def delete(slug):
    post = Posts.query.filter(Posts.slug==slug).first()
    if not post:
        flash("Post does not exist", category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash("Post was Deleted", category='danger')
    return redirect(url_for('blog.posts'))


@bp.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get("text")
    if not text:
        flash("Comment cannot be empty", category="error")
    else:
        post = Posts.query.filter(Posts.id == post_id).first()
        if not post:
            flash("Post does not exist.", category="error")
        else:
            comment = Comment(text=text, author=current_user.id, post_id=post_id)
            flash("Commet Added.", category="success")
            db.session.add(comment)
            db.session.commit()
    return redirect(url_for("blog.posts"))
        
@bp.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter(Comment.id==comment_id).first()

    if not comment:
        flash("Comment Does not exist.", category="error")
    elif not (current_user.id == comment.author or current_user.id == comment.post.author or current_user.is_admin):
        flash("You do not have permission to delete this comment", category="error")
    else:
        db.session.delete(comment)
        db.session.commit()
        flash("Comment deleted.", category="success")
    return redirect(url_for("blog.posts"))

@bp.route("/like-post/<post_id>", methods=['POST'])
@login_required
def like(post_id):
    post = Posts.query.filter(Posts.id == post_id).first()
    liked = Like.query.filter(Like.author==current_user.id, Like.post_id==post_id).first()

    if not post:
        return jsonify({'error': 'Post Does not exist.'}, 400)
    elif liked:
        db.session.delete(liked)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
    
    return jsonify({"likes":len(post.likes), "liked": current_user.id in [l.author for l in post.likes]})