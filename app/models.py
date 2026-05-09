from datetime import datetime, timezone
from app import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.LargeBinary(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_2fa_enabled = db.Column(db.Boolean, default=False)
    totp_secret = db.Column(db.String(32), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime, nullable=True)
    failed_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'


class LoginAttempt(db.Model):
    __tablename__ = 'login_attempts'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    success = db.Column(db.Boolean, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_agent = db.Column(db.String(256), nullable=True)

    def __repr__(self):
        return f'<LoginAttempt {self.email} at {self.timestamp}>'
