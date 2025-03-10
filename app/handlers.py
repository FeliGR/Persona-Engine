"""
Flask Application Handlers Module

This module provides error handling, request hooks, and shutdown handlers for the
Flask application. It includes functions for registering custom error handlers to
provide consistent JSON responses for different error types, request processing
middleware to track performance metrics, and graceful shutdown procedures.

These handlers ensure the application maintains consistent behavior, proper logging,
and clean resource management throughout its lifecycle.
"""

import atexit
import time

from flask import Flask, g, jsonify, request
from werkzeug.exceptions import HTTPException

from adapters.loggers.logger_adapter import app_logger


def register_error_handlers(app: Flask) -> None:
    """
    Register custom error handlers for the Flask application.

    This function sets up handlers for common HTTP errors and exceptions, ensuring
    that all errors return properly formatted JSON responses with appropriate status
    codes, maintaining API consistency even during error conditions.

    Args:
        app (Flask): The Flask application instance to register handlers with.
    """

    @app.errorhandler(400)
    def handle_bad_request(error):
        app_logger.error("Bad request: %s", error)
        return jsonify({"error": "Bad request", "message": str(error)}), 400

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"error": "Resource not found", "message": str(error)}), 404

    @app.errorhandler(429)
    def handle_rate_limit_exceeded(error):
        app_logger.error("Rate limit exceeded: %s", error)
        return jsonify({"error": "Too many requests", "message": str(error)}), 429

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        app_logger.error("HTTP exception: %s", error)
        return jsonify({"error": error.name, "message": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_exception(error):
        app_logger.error("Unhandled exception: %s", str(error), exc_info=True)
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
    """
    Register request processing hooks for the Flask application.

    This function sets up before_request and after_request hooks to track request
    processing time and log request details, helping with performance monitoring
    and request debugging.

    Args:
        app (Flask): The Flask application instance to register hooks with.
    """

    @app.before_request
    def before_request():
        g.start_time = time.time()
        app_logger.debug("Request started: %s %s", request.method, request.path)

    @app.after_request
    def after_request(response):
        if hasattr(g, "start_time"):
            elapsed = time.time() - g.start_time
            app_logger.info(
                "Request completed: %s %s - Status: %s - Time: %.4fs",
                request.method,
                request.path,
                response.status_code,
                elapsed,
            )
        return response


def register_shutdown_handlers(_app: Flask) -> None:
    """
    Register application shutdown handlers.

    This function sets up handlers that execute during application shutdown,
    ensuring graceful termination and proper cleanup of resources.

    Args:
        _app (Flask): The Flask application instance (unused, but kept for future use).
    """

    def on_exit():
        app_logger.info("Application shutting down")

    atexit.register(on_exit)
