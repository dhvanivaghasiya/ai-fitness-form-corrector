"""
AI Fitness Form Corrector — Flask Application Entry Point
"""
from flask import Flask
from flask_login import LoginManager
from config import Config
from backend.models import db
from backend.models.user import User

login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from backend.auth.routes import auth_bp
    from backend.dashboard.routes import dashboard_bp
    from backend.workout.routes import workout_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='')
    app.register_blueprint(workout_bp, url_prefix='/workout')

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
