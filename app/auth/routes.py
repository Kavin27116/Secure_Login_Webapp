from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timezone, timedelta

from app import db, limiter
from app.auth import auth
from app.auth.forms import RegistrationForm, LoginForm, TwoFactorForm, Setup2FAForm
from app.auth.helpers import (
    hash_password, verify_password,
    generate_totp_secret, get_totp_uri,
    verify_totp, generate_qr_code_b64,
    is_account_locked, lockout_remaining_seconds,
)
from app.models import User, LoginAttempt

MAX_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


def _log_attempt(email, success):
    attempt = LoginAttempt(
        email=email,
        ip_address=request.remote_addr or '0.0.0.0',
        success=success,
        user_agent=(request.user_agent.string or '')[:256],
    )
    db.session.add(attempt)
    db.session.commit()


# ─── Register ────────────────────────────────────────────────────────────────

@auth.route('/register', methods=['GET', 'POST'])
@limiter.limit("20 per hour")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        username = form.username.data.strip()

        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists.', 'danger')
            return render_template('auth/register.html', form=form)

        if User.query.filter_by(username=username).first():
            flash('This username is already taken.', 'danger')
            return render_template('auth/register.html', form=form)

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(form.password.data),
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please sign in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


# ─── Login ────────────────────────────────────────────────────────────────────

@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()

        if user is None:
            _log_attempt(email, False)
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html', form=form)

        if is_account_locked(user):
            secs = lockout_remaining_seconds(user)
            flash(f'Account locked. Try again in {secs // 60}m {secs % 60}s.', 'danger')
            return render_template('auth/login.html', form=form)

        if not verify_password(form.password.data, user.password_hash):
            user.failed_attempts += 1
            if user.failed_attempts >= MAX_ATTEMPTS:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_MINUTES)
                flash(f'Too many failed attempts. Account locked for {LOCKOUT_MINUTES} minutes.', 'danger')
            else:
                left = MAX_ATTEMPTS - user.failed_attempts
                flash(f'Invalid email or password. {left} attempt(s) remaining.', 'danger')
            db.session.commit()
            _log_attempt(email, False)
            return render_template('auth/login.html', form=form)

        # Correct password — reset lockout counters
        user.failed_attempts = 0
        user.locked_until = None
        db.session.commit()

        if user.is_2fa_enabled:
            session['pre_2fa_user_id'] = user.id
            session['remember_me'] = form.remember_me.data
            return redirect(url_for('auth.two_factor'))

        login_user(user, remember=form.remember_me.data)
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()
        _log_attempt(email, True)

        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('dashboard.index')
        return redirect(next_page)

    return render_template('auth/login.html', form=form)


# ─── 2FA Verify ──────────────────────────────────────────────────────────────

@auth.route('/2fa', methods=['GET', 'POST'])
def two_factor():
    user_id = session.get('pre_2fa_user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)
    if not user:
        session.pop('pre_2fa_user_id', None)
        return redirect(url_for('auth.login'))

    form = TwoFactorForm()
    if form.validate_on_submit():
        if verify_totp(user.totp_secret, form.token.data.strip()):
            remember = session.pop('remember_me', False)
            session.pop('pre_2fa_user_id', None)
            login_user(user, remember=remember)
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            _log_attempt(user.email, True)
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid authentication code. Please try again.', 'danger')

    return render_template('auth/two_factor.html', form=form)


# ─── Setup 2FA ───────────────────────────────────────────────────────────────

@auth.route('/setup-2fa', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    if current_user.is_2fa_enabled:
        flash('Two-Factor Authentication is already enabled.', 'info')
        return redirect(url_for('dashboard.index'))

    if 'temp_totp_secret' not in session:
        session['temp_totp_secret'] = generate_totp_secret()

    secret = session['temp_totp_secret']
    uri = get_totp_uri(secret, current_user.email)
    qr_b64 = generate_qr_code_b64(uri)

    form = Setup2FAForm()
    if form.validate_on_submit():
        if verify_totp(secret, form.token.data.strip()):
            current_user.totp_secret = secret
            current_user.is_2fa_enabled = True
            db.session.commit()
            session.pop('temp_totp_secret', None)
            flash('Two-Factor Authentication enabled successfully!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid code. Please scan the QR code again and retry.', 'danger')

    return render_template('auth/setup_2fa.html', form=form, qr_b64=qr_b64, secret=secret)


# ─── Disable 2FA ─────────────────────────────────────────────────────────────

@auth.route('/disable-2fa', methods=['POST'])
@login_required
def disable_2fa():
    current_user.is_2fa_enabled = False
    current_user.totp_secret = None
    db.session.commit()
    flash('Two-Factor Authentication has been disabled.', 'warning')
    return redirect(url_for('dashboard.index'))


# ─── Logout ───────────────────────────────────────────────────────────────────

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been signed out securely.', 'success')
    return redirect(url_for('auth.login'))
