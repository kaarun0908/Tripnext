import os
from flask import Flask, render_template
from config import config
from app.extensions import db, migrate, login_manager, csrf

def create_app(config_name=None):
    """Application factory for TripNest."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from app.auth import auth_bp
    from app.main import main_bp
    from app.bookings import bookings_bp
    from app.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(admin_bp)

    # Context processors & template filters
    @app.context_processor
    def inject_global_data():
        from datetime import datetime, timezone
        return {
            'current_year': datetime.now(timezone.utc).year,
            'app_name': 'TripNest'
        }

    @app.template_filter('inr')
    def format_inr(value):
        try:
            val = float(value)
            return f"₹{val:,.2f}"
        except (ValueError, TypeError):
            return f"₹{value}"

    # Error handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # Auto-initialize and seed database if empty
    with app.app_context():
        try:
            from app.models import Destination
            db.create_all()
            if not Destination.query.first():
                from scripts.seed_data import run_seed
                run_seed()
        except Exception as e:
            app.logger.warning(f"Auto-migration/seed deferred: {e}")

    return app
