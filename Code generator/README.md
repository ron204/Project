# Secure Code Generator

A polished Flask portfolio project that demonstrates the verification-code stage of an account-registration or login flow. It securely generates numeric and alphanumeric codes, then verifies a temporary code locally with expiry, attempt limits, and one-time use. It does not connect to real accounts, email, SMS, or authentication providers.

## Features

- Cryptographically secure numeric and uppercase alphanumeric code generation using Python's `secrets` module.
- Configurable code lengths from 4 to 64 characters.
- Responsive interface with copy, generate-new, validation, accessible labels, and clear status messages.
- Live countdown timer that disables verification when a temporary code expires.
- Local verification flow with salted PBKDF2-HMAC-SHA256 hashes, constant-time comparison, five-attempt protection, expiry, and one-time use.
- Automated unit and Flask route tests.

## Technology Stack

Python 3.10+, Flask, Jinja templates, vanilla JavaScript, CSS, `secrets`, `hashlib`, `hmac`, and Pytest.

## Architecture

```text
Code generator/
├── app.py                    # Flask routes and UI orchestration
├── config.py                 # Application and security limits
├── generator/code_generator.py
│                             # Validated secrets-based code generation
├── verification/verifier.py  # Hashing, state, expiry, and attempt controls
├── templates/                # Server-rendered accessible pages
├── static/css/style.css      # Responsive presentation layer
├── static/js/app.js          # Countdown, copy, and async verification UX
└── tests/                    # Unit and route-level automated tests
```

`app.py` coordinates requests without embedding security logic. `CodeGenerator` creates a code from OS-backed entropy. For a verification request, `VerificationService` stores only a salted derived hash plus non-sensitive metadata. The browser receives the code once for this local demonstration and only receives status, expiry, and remaining-attempt information afterwards.

## Security Features

- Uses `secrets.choice`, not the predictable `random` module.
- Stores verification codes as a salted PBKDF2-HMAC-SHA256 derived hash with 200,000 iterations.
- Uses `hmac.compare_digest` for constant-time hash comparison.
- Applies an expiration period and removes expired entries.
- Limits failed verification attempts and invalidates a code after the final failure.
- Consumes successful codes immediately, preventing reuse.
- Keeps all verification data in memory for the local demonstration; restarting the app removes it.

This is intentionally a local, educational demonstration. A production implementation should add HTTPS, CSRF protection, a TTL-backed datastore such as Redis, delivery-provider integration, rate limiting by account/IP, and carefully redacted audit logs.

## How Verification Works

1. The user selects a code type, length, and expiration period.
2. The app generates a cryptographically secure code and displays it once.
3. The verifier creates a random salt and stores a PBKDF2-HMAC hash—not the plaintext code.
4. The browser shows a countdown and submits a candidate value for checking.
5. The server rejects empty, incorrect, expired, locked, and previously consumed codes; a correct code is immediately invalidated.

## Installation

```powershell
cd "Code generator"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first. Set a durable session key before using the app outside development:

```powershell
$env:FLASK_SECRET_KEY = "a-long-random-secret-value"
```

## Run the Application

```powershell
python app.py
```

On Windows, you can also double-click `Start Code Generator.bat`. It uses this
project's `.venv`, opens `http://127.0.0.1:5000` in your default browser, and
keeps the command window open while the local server is running. A desktop
shortcut can point to that file; its **Start in** value does not matter.

Open `http://127.0.0.1:5000` in a browser. Choose **Temporary verification code**, generate a six-digit code, try an incorrect value, and then submit the displayed code. Generate another code and wait for the one-minute timer to observe expiry.

## Run Tests

```powershell
python -m pytest -q
```

## Example Usage

Select **Temporary verification code**, **Numeric**, **6** characters, and **1 minute**. The app displays the code and a `00:59`-style countdown. The verification area reports each failed attempt, locks after five failures, and confirms a valid code only once.

## What I Learned

- Separated web routing, generation policy, and verification state into focused modules.
- Used CSPRNG APIs, salted key derivation, and constant-time comparisons to model secure temporary-code handling.
- Built a responsive accessible Flask interface with progressive server rendering and JavaScript-enhanced verification feedback.
- Wrote unit and route-level tests for security rules and important user flows.

## Future Improvements

- Add CSRF protection and production-grade configuration validation.
- Use Redis or a database with TTL for distributed, durable verification state.
- Add browser end-to-end tests and structured security-event logging without sensitive values.
- Containerize the app and deploy behind HTTPS with a production WSGI server.

## CV Description

- Built a Flask-based secure verification-code demonstration using Python CSPRNG primitives, PBKDF2-HMAC hashing, constant-time comparison, expiry controls, and one-time token invalidation.
- Designed a responsive verification workflow with a real-time client-side countdown, bounded failed-attempt handling, accessible form controls, and automated Pytest coverage.
- Applied modular backend design by separating generation policy, verification state management, Flask routing, and presentation-layer concerns.
