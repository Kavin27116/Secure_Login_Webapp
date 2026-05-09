import bcrypt
import pyotp
import qrcode
import io
import base64
from datetime import datetime, timezone


def hash_password(password: str) -> bytes:
    """Hash a password using bcrypt with a random salt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt)


def verify_password(password: str, password_hash) -> bool:
    """Verify plaintext password against stored bcrypt hash."""
    if isinstance(password_hash, str):
        password_hash = password_hash.encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), password_hash)


def generate_totp_secret() -> str:
    """Generate a cryptographically random TOTP base32 secret."""
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str) -> str:
    """Build TOTP provisioning URI for QR code."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name='SecureLoginApp')


def verify_totp(secret: str, token: str) -> bool:
    """Verify a 6-digit TOTP token (allows ±1 window = 90s tolerance)."""
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)


def generate_qr_code_b64(uri: str) -> str:
    """Return QR code PNG as base64 string for embedding in HTML."""
    qr = qrcode.QRCode(version=1, box_size=8, border=4)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0a0a0f", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def is_account_locked(user) -> bool:
    """Return True if the user is currently locked out."""
    if user.locked_until is None:
        return False
    now = datetime.now(timezone.utc)
    lu = user.locked_until
    if lu.tzinfo is None:
        lu = lu.replace(tzinfo=timezone.utc)
    return now < lu


def lockout_remaining_seconds(user) -> int:
    """Return seconds remaining on a lockout (0 if not locked)."""
    if user.locked_until is None:
        return 0
    now = datetime.now(timezone.utc)
    lu = user.locked_until
    if lu.tzinfo is None:
        lu = lu.replace(tzinfo=timezone.utc)
    return max(0, int((lu - now).total_seconds()))
