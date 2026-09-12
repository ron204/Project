"""Flask entry point for the local Secure Code Generator demonstration."""

from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

from config import Config
from generator.code_generator import CodeGenerator, InvalidCodeConfiguration
from verification.verifier import VerificationResult, VerificationService


def create_app(config_class: type[Config] = Config) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.extensions["verifier"] = VerificationService()

    def page_context(**extra: object) -> dict[str, object]:
        return {"limits": app.config, **extra}

    @app.get("/")
    def index():
        return render_template("index.html", **page_context())

    @app.post("/generate")
    def generate():
        code_type = request.form.get("code_type", "numeric")
        length = request.form.get("length", type=int)
        expires_in = request.form.get("expires_in", type=int)
        purpose = request.form.get("purpose", "suggested")

        try:
            code = CodeGenerator.generate(code_type, length)
        except InvalidCodeConfiguration as error:
            flash(str(error), "error")
            return redirect(url_for("index"))

        verification = None
        if purpose == "verification":
            if expires_in not in app.config["ALLOWED_EXPIRATIONS"]:
                flash("Choose one of the available expiration periods.", "error")
                return redirect(url_for("index"))
            verification_id = str(uuid4())
            verifier = app.extensions["verifier"]
            verifier.create(
                verification_id,
                code,
                expires_in=timedelta(minutes=expires_in),
                max_attempts=app.config["MAX_VERIFICATION_ATTEMPTS"],
            )
            verification = {"id": verification_id, **verifier.status(verification_id).as_dict()}

        return render_template(
            "index.html",
            **page_context(
            generated_code=code,
            code_type=code_type,
            length=length,
            verification=verification,
            expires_in=expires_in,
            purpose=purpose,
            ),
        )

    @app.post("/verify")
    def verify():
        verification_id = request.form.get("verification_id", "")
        submitted_code = request.form.get("submitted_code", "")
        result: VerificationResult = app.extensions["verifier"].verify(verification_id, submitted_code)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(result.as_dict())

        category = "success" if result.success else "error"
        flash(result.message, category)
        verification = None
        if result.status == "active":
            verification = {"id": verification_id, **result.as_dict()}
        return render_template("index.html", **page_context(verification=verification))

    return app


if __name__ == "__main__":
    create_app().run()
