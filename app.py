"""
Main Application Entry Point
Flask Application Factory, Blueprint Registration & Server Execution.
"""

import os
from flask import Flask, render_template
from flask_cors import CORS
from config import Config
from database import db, User, Station, SensorReading, WaterQuality, Forecast, Alert, SatelliteData
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.api import api_bp
from routes.admin import admin_bp
from routes.reports import reports_bp

def init_db(app):
    """Ensures database directory exists, creates tables, and seeds baseline demo accounts if missing."""
    with app.app_context():
        os.makedirs(os.path.dirname(Config.DB_PATH), exist_ok=True)
        db.create_all()

        # Seed baseline demo accounts if admin user does not exist
        admin = User.query.filter_by(email="admin@ganga.gov.in").first()
        if not admin:
            print("Seeding baseline demo accounts into SQLite database...")
            # If a researcher account with email admin@ganga.gov.in existed from previous auto-create, update it
            existing_user = User.query.filter_by(email="admin@ganga.gov.in").first()
            if existing_user:
                existing_user.role = "Administrator"
                existing_user.name = "System Administrator"
                existing_user.set_password("Admin@123")
            else:
                u_admin = User(name="System Administrator", email="admin@ganga.gov.in", role="Administrator")
                u_admin.set_password("Admin@123")
                db.session.add(u_admin)

            if not User.query.filter_by(email="analyst@ganga.gov.in").first():
                u_analyst = User(name="Dr. Ananya Sharma", email="analyst@ganga.gov.in", role="Environmental Analyst")
                u_analyst.set_password("Analyst@123")
                db.session.add(u_analyst)

            if not User.query.filter_by(email="researcher@ganga.gov.in").first():
                u_researcher = User(name="Prof. Rajesh Kumar", email="researcher@ganga.gov.in", role="Researcher")
                u_researcher.set_password("Research@123")
                db.session.add(u_researcher)

            db.session.commit()

        # Seed default stations if missing
        if Station.query.count() == 0:
            for s in Config.STATIONS:
                st = Station(id=s['id'], name=s['name'], latitude=s['lat'], longitude=s['lng'], location=s['location'], status='ACTIVE')
                db.session.add(st)
            db.session.commit()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS
    CORS(app)

    # Initialize extensions
    db.init_app(app)

    # Automatically ensure database tables & baseline demo accounts exist before handling any routes
    init_db(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(reports_bp)

    # Context processors for template rendering
    @app.context_processor
    def inject_user():
        from flask import session
        return dict(
            current_user_name=session.get('user_name'),
            current_user_email=session.get('user_email'),
            current_user_role=session.get('user_role'),
            is_logged_in='user_id' in session
        )

    # Global 404 & 500 error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Database Path: {Config.DB_PATH}")
    print(f"Starting Ganga Water Quality DSS Server on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
