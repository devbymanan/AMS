import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, redirect, url_for, render_template
from config import Config
from extensions import db, login_manager
from models.models import User
from flask_login import current_user

# Import blueprints
from routes.dashboard import bp as dashboard_bp
from routes.shifts import bp as shifts_bp
from routes.devices import bp as devices_bp
from routes.employees import bp as employees_bp
from routes.attendance import bp as attendance_bp
from routes.reports import bp as reports_bp
from routes.roster import bp as roster_bp
from routes.auth import bp as auth_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Logging setup
    if not os.path.exists("logs"):
        os.mkdir("logs")
    file_handler = RotatingFileHandler(
        "logs/ams.log", maxBytes=10240000, backupCount=10
    )
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )
    )
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info("AMS startup")

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(shifts_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(roster_bp)
    app.register_blueprint(auth_bp)

    with app.app_context():
        # Creates tables that don't exist yet (e.g., Users)
        db.create_all()

    @app.before_request
    def check_valid_login():
        if not current_user.is_authenticated:
            if (
                request.endpoint
                and not request.endpoint.startswith("auth.")
                and "static" not in request.endpoint
            ):
                return redirect(url_for("auth.login", next=request.url))

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f"Server Error: {error}")
        return render_template("500.html"), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
