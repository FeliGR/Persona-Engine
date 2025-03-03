from flask import Flask, request, g, jsonify
from werkzeug.exceptions import HTTPException
import atexit
import time
from utils.logger import logger


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(400)
    def handle_bad_request(error):
        logger.warning(f"Bad request: {error}")
        return jsonify({"error": "Bad request", "message": str(error)}), 400

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"error": "Resource not found", "message": str(error)}), 404

    @app.errorhandler(429)
    def handle_rate_limit_exceeded(error):
        logger.warning(f"Rate limit exceeded: {error}")
        return jsonify({"error": "Too many requests", "message": str(error)}), 429

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        logger.error(f"HTTP exception: {error}")
        return jsonify({"error": error.name, "message": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
        return (
            jsonify(
                {
                    "error": "Internal server error",
                    "message": "An unexpected error occurred",
                }
            ),
            500,
        )


def register_request_hooks(app: Flask) -> None:
    @app.before_request
    def before_request():
        g.start_time = time.time()
        logger.debug(f"Request started: {request.method} {request.path}")

    @app.after_request
    def after_request(response):
        if hasattr(g, "start_time"):
            elapsed = time.time() - g.start_time
            logger.info(
                f"Request completed: {request.method} {request.path} - Status: {response.status_code} - Time: {elapsed:.4f}s"
            )
        return response


def register_shutdown_handlers(app: Flask) -> None:
    def on_exit():
        logger.info("Application shutting down")

    atexit.register(on_exit)
