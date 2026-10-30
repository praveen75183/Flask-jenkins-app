import logging

from flask import Flask

from app.config import get_config


def create_app(config_name=None):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    logging.basicConfig(
        level=app.config["LOG_LEVEL"],
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    from app.routes import bp

    app.register_blueprint(bp)

    return app
