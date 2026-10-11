from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models.models import User
from extensions import db
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    try:
        # Create default admin if Users table is empty
        if User.query.count() == 0:
            admin = User(
                username="admin", password_hash=generate_password_hash("admin123")
            )
            db.session.add(admin)
            db.session.commit()
    except Exception:
        pass

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard.dashboard"))

        flash("Invalid username or password")
    return render_template("login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
