import time

from flask import Flask, jsonify


def register_routes(app: Flask) -> None:
    @app.route("/")
    def index():
        return jsonify(
            {
                "status": "ok",
                "service": "persona-engine",
                "version": app.config.get("VERSION", "0.1.0"),
            }
        )

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy", "timestamp": time.time()})
