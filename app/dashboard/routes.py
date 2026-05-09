from flask import render_template
from flask_login import login_required, current_user
from app.models import LoginAttempt
from app.dashboard import dashboard


@dashboard.route('/')
@login_required
def index():
    recent_attempts = (
        LoginAttempt.query
        .filter_by(email=current_user.email)
        .order_by(LoginAttempt.timestamp.desc())
        .limit(10)
        .all()
    )
    return render_template('dashboard/index.html', recent_attempts=recent_attempts)
