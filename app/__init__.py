from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_session import Session
from config import Config

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)
sess = Session()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    sess.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please sign in to access this page.'
    login_manager.login_message_category = 'warning'

    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from app.dashboard import dashboard as dashboard_blueprint
    app.register_blueprint(dashboard_blueprint, url_prefix='/dashboard')

    from flask import redirect, url_for

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app
