# Secure Login System — Web Application

> **Final Year Project | Department of Computer Science and Engineering**
> Academic Year: 2025 – 2026

---

## Abstract

This project presents the design and implementation of a **Secure Login Web Application** that addresses common vulnerabilities in modern authentication systems. The system incorporates industry-standard cryptographic password hashing, robust input validation, SQL injection prevention, and stateful session management. An optional Two-Factor Authentication (2FA) layer provides an additional barrier against unauthorized access.

The goal of this project is to demonstrate how fundamental cybersecurity principles can be applied in a real-world web environment to protect user credentials and sensitive session data.

---

## Table of Contents

- [Abstract](#abstract)
- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Security Mechanisms](#security-mechanisms)
- [Installation and Setup](#installation-and-setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)
- [Future Enhancements](#future-enhancements)
- [References](#references)
- [Author](#author)

---

## Project Overview

Authentication is the first line of defense for any web application. Weak or poorly implemented login systems are among the most exploited vulnerabilities in cybersecurity. This project builds a **production-ready secure login system** that implements:

- Hashed password storage using **bcrypt / Argon2**
- **Parameterized queries** to block SQL injection attacks
- Secure, server-side **session management** with expiration and logout
- Optional **Time-based One-Time Password (TOTP)** Two-Factor Authentication
- Input sanitization and validation at every entry point

This system is built with real-world threat models in mind, including brute-force attacks, credential stuffing, session hijacking, and injection attacks.

---

## Key Features

| Feature | Description |
|---|---|
| **User Registration** | Secure sign-up with email validation and duplicate detection |
| **Password Hashing** | Passwords are never stored in plaintext — bcrypt with salt rounds or Argon2id |
| **Login Authentication** | Secure credential verification against hashed values |
| **SQL Injection Protection** | All database interactions use parameterized / prepared statements |
| **Session Management** | Server-side sessions with secure cookies, CSRF protection, and auto-expiry |
| **Logout** | Full session invalidation and secure cookie clearance on logout |
| **2FA (Optional)** | TOTP-based Two-Factor Authentication via Google Authenticator or Authy |
| **Account Lockout** | Temporary lockout after a configurable number of failed login attempts |
| **Rate Limiting** | Per-IP request throttling to prevent brute-force attacks |
| **Password Strength Meter** | Real-time frontend feedback on password strength |

---

## System Architecture

```
┌───────────────────────────────────────────────────┐
│                   CLIENT BROWSER                  │
│  ┌───────────┐   ┌────────────┐  ┌─────────────┐ │
│  │ Register  │   │   Login    │  │  Dashboard  │ │
│  │   Form    │   │   Form     │  │  (Protected)│ │
│  └─────┬─────┘   └─────┬──────┘  └──────┬──────┘ │
└────────┼───────────────┼────────────────┼─────────┘
         │  HTTPS        │                │
┌────────▼───────────────▼────────────────▼─────────┐
│                  WEB SERVER (Flask / Node)         │
│                                                   │
│  ┌──────────────┐    ┌──────────────────────────┐ │
│  │  Input       │    │   Session Middleware      │ │
│  │  Validator   │    │   (CSRF, Cookie Flags)   │ │
│  └──────┬───────┘    └──────────────────────────┘ │
│         │                                         │
│  ┌──────▼───────────────────────────────────────┐ │
│  │         Authentication Engine                │ │
│  │  - bcrypt / Argon2 hash comparison           │ │
│  │  - 2FA TOTP verification (pyotp / speakeasy) │ │
│  │  - Account lockout logic                     │ │
│  └──────┬───────────────────────────────────────┘ │
└─────────┼──────────────────────────────────────────┘
          │  Parameterized Queries
┌─────────▼──────────────────────────────────────────┐
│                   DATABASE LAYER                   │
│          SQLite / PostgreSQL / MySQL               │
│  ┌──────────┐  ┌────────────┐  ┌────────────────┐  │
│  │  users   │  │  sessions  │  │  login_attempts│  │
│  └──────────┘  └────────────┘  └────────────────┘  │
└────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend
- **Python 3.11+** with **Flask** framework (or Node.js / Express)
- **bcrypt** / **Argon2-cffi** — password hashing
- **Flask-Session** — server-side session management
- **Flask-WTF** — CSRF protection and form validation
- **pyotp** — TOTP-based 2FA
- **qrcode** — QR code generation for 2FA setup
- **SQLAlchemy** — ORM with parameterized query support

### Database
- **SQLite** (development) / **PostgreSQL** (production)

### Frontend
- **HTML5**, **CSS3** (vanilla), **JavaScript (ES6+)**
- **Google Fonts** — Inter / Poppins typography
- Custom password strength meter

### Security Libraries
| Library | Purpose |
|---|---|
| `bcrypt` | Password hashing with adaptive cost factor |
| `argon2-cffi` | Argon2id — memory-hard hashing algorithm |
| `flask-limiter` | Rate limiting per IP |
| `flask-talisman` | HTTP security headers (CSP, HSTS, etc.) |
| `pyotp` | RFC 6238 TOTP standard for 2FA |

---

## Security Mechanisms

### 1. Password Hashing — bcrypt / Argon2
Passwords are **never stored in plaintext**. On registration, the password is passed through a one-way cryptographic hash function with a randomly generated salt.

```python
import bcrypt

# On Registration
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))

# On Login
is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash)
```

Alternatively, **Argon2id** (winner of the Password Hashing Competition) is used:
```python
from argon2 import PasswordHasher

ph = PasswordHasher(time_cost=2, memory_cost=65536, parallelism=2)
hash = ph.hash(password)
ph.verify(hash, password)  # raises exception on mismatch
```

### 2. SQL Injection Prevention
All database queries use **parameterized statements** — user input is never interpolated directly into SQL strings.

```python
# VULNERABLE (never do this)
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")

# SECURE — parameterized query
cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
```

### 3. Session Management
- Sessions are stored **server-side** (filesystem or Redis).
- Cookies are set with `HttpOnly`, `Secure`, and `SameSite=Strict` flags.
- Sessions expire after a configurable idle timeout.
- On logout, the session is **fully invalidated** on the server.

### 4. Two-Factor Authentication (TOTP)
- On 2FA enrollment, a **secret key** is generated and linked to the user.
- A **QR code** is shown for scanning with Google Authenticator / Authy.
- On every login, users must enter the current 6-digit TOTP code.
- TOTP codes are time-limited to **30 seconds** per the RFC 6238 standard.

```python
import pyotp

secret = pyotp.random_base32()
totp = pyotp.TOTP(secret)
totp.verify(user_input_code)  # True / False
```

### 5. Additional Protections
- **CSRF Tokens** on all forms via Flask-WTF
- **Account lockout** after 5 consecutive failed attempts (15-minute cooldown)
- **Rate limiting** — max 10 login attempts per minute per IP
- **HTTP Security Headers** — X-Frame-Options, Content-Security-Policy, HSTS
- **Password strength enforcement** — minimum length, complexity rules

---

## Installation and Setup

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- Git

### Step 1 — Clone the Repository
```bash
git clone https://github.com/<your-username>/Secure_Login_Webapp.git
cd Secure_Login_Webapp
```

### Step 2 — Create a Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Configure Environment Variables
Create a `.env` file in the project root:
```env
SECRET_KEY=your_very_long_random_secret_key_here
DATABASE_URL=sqlite:///secure_login.db
SESSION_TYPE=filesystem
BCRYPT_ROUNDS=12
ENABLE_2FA=true
FLASK_ENV=development
```

> **Note:** Generate a strong secret key with:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

### Step 5 — Initialize the Database
```bash
python init_db.py
```

### Step 6 — Run the Application
```bash
flask run
```

Open your browser and navigate to: `http://localhost:5000`

---

## Usage

### User Registration
1. Navigate to `/register`
2. Enter a valid email address and a strong password
3. The password strength meter provides real-time feedback
4. On success, you are redirected to the login page

### User Login
1. Navigate to `/login`
2. Enter registered credentials
3. If 2FA is enabled, enter the 6-digit code from your authenticator app
4. On success, you are redirected to the protected dashboard

### Enable Two-Factor Authentication
1. Log in and navigate to `/settings/2fa`
2. Scan the displayed QR code with Google Authenticator or Authy
3. Enter the generated 6-digit code to confirm enrollment
4. 2FA is now active for your account

### Logout
- Click the **Logout** button on the dashboard
- The session is fully destroyed server-side

---

## Project Structure

```
Secure_Login_Webapp/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models.py            # User, Session, LoginAttempt models
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py        # Register, Login, Logout routes
│   │   ├── forms.py         # WTForms with validation
│   │   └── helpers.py       # Password hashing, 2FA utilities
│   ├── dashboard/
│   │   ├── __init__.py
│   │   └── routes.py        # Protected routes
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── password_strength.js
│   └── templates/
│       ├── base.html
│       ├── auth/
│       │   ├── login.html
│       │   ├── register.html
│       │   └── setup_2fa.html
│       └── dashboard/
│           └── index.html
├── migrations/              # Database migration files
├── tests/
│   ├── test_auth.py         # Unit tests for authentication
│   ├── test_2fa.py          # Unit tests for TOTP
│   └── test_sql_injection.py
├── init_db.py               # Database initialization script
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
├── config.py                # Application configuration
└── README.md
```

---

## Screenshots

> *(Screenshots to be added after UI implementation)*

| Page | Description |
|---|---|
| Registration Page | Form with real-time password strength meter |
| Login Page | Email + password with 2FA code field |
| 2FA Setup | QR code display and verification |
| Dashboard | Protected page shown after successful login |

---

## Future Enhancements

- OAuth 2.0 / Social login (Google, GitHub)
- Email verification on registration
- Password reset via secure email link
- Admin dashboard for user management
- Persistent login with Remember-Me tokens (secure, hashed)
- WebAuthn / Passkey support (FIDO2)
- Audit log for all authentication events
- Docker containerization for easy deployment

---

## References

1. OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
2. OWASP Session Management Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
3. NIST Digital Identity Guidelines (SP 800-63B) — https://pages.nist.gov/800-63-3/sp800-63b.html
4. RFC 6238 — TOTP: Time-Based One-Time Password Algorithm — https://tools.ietf.org/html/rfc6238
5. Argon2 — Memory-Hard Password Hashing — https://github.com/P-H-C/phc-winner-argon2
6. Flask Documentation — https://flask.palletsprojects.com/
7. bcrypt — Password Hashing Library — https://pypi.org/project/bcrypt/

---

## Author

**[Your Name]** — Final Year Student, B.E. Computer Science and Engineering
- GitHub: [@your-github-username](https://github.com/your-github-username)
- Email: your.email@example.com

> *This project was developed as part of the Final Year Academic Project requirement for the degree of Bachelor of Engineering in Computer Science and Engineering.*

---

## License

This project is developed for academic purposes. All rights reserved.

---

*Last Updated: May 2026*
