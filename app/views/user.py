from flask import Blueprint, render_template, url_for, request, redirect, flash
from ..extensions import db
from ..models import Users
from flask_login import LoginManager, logout_user, login_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('users', __name__)
login_manager = LoginManager()

@login_manager.user_loader
def user_loader(user_id):
    user = Users.query.get(int(user_id))
    return user

@bp.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username:
            flash("Username is Missing.", category="error")
        elif not email:
            flash("Email is Missing.", category="error")
        elif not password:
            flash("Password is Missing.", category="error")
        else:
            check_email = Users.query.filter(Users.email==email).first()
            if check_email:
                flash("A User has already has registered using this email", category='error')
            else:
                user = Users(username=username, email=email, password=generate_password_hash(password))
                db.session.add(user)
                db.session.commit()
                flash("User registered Successfully.", category="success")
                print(f"username: {username}, email: {email}, passowrd: {password}")
                return redirect(url_for("users.login"))
    
    
    return render_template('users/register.html')

@bp.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        if not email:
            flash("Email is required", category='error')
        elif not password:
            flash("Password is required", category='error')
        else:
            user = Users.query.filter(Users.email==email).first()
            if not user:
                flash("User with that email does not Exisit", category='error')
            elif not check_password_hash(user.password, password):
                flash("Password is incorrect", category='error')
            else:
                flash("Login is Successful", category='success')
                login_user(user)
    return render_template('users/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Successful", category='success')
    return redirect(url_for('users.login'))