from flask import Flask, render_template, jsonify
from flask_cors import CORS
from flask_mail import Mail
from flask_apscheduler import APScheduler
from config import Config
from app.models import db, bcrypt

mail = Mail()
scheduler = APScheduler()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    #Enable CORS across all origins for local API testing
    CORS(app)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.products import products_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)

    # ROOT ROUTE TO SERVE THE DASHBOARD
    @app.route('/')
    def index():
        return render_template('index.html')

    #PUBLIC HEALTH CHECK (Allows the frontend to verify backend connectivity)
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'ok', 'message': 'Flask Backend is running'}), 200

    #Application Context Block
    with app.app_context():
        # Ensure database tables exist upon startup
        db.create_all()

        # Initialize and configure APScheduler wihthin application context
        if not scheduler.running:
            scheduler.init_app(app)

            # Import task function
            from app.utils.scheduler_tasks import check_expiring_products_job

            # Add cron job to run every day at 08:00 AM UTC
            # (For local testing, change 'trigger' to 'interval', seconds=60)
            scheduler.add_job(
                id='daily_expiry_check',
                func=check_expiring_products_job,
                args=[app, mail],
                trigger='cron',
                hour=8,
                minute=0
            )

            scheduler.start()

    return app