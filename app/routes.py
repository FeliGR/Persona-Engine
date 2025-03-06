"""
Flask Application Routes Module

This module defines the base application routes including the index and health check
endpoints. These routes provide basic information about the service status and version,
which is useful for monitoring, deployments, and service discovery.

The routes registered here are separate from the API blueprint routes and serve
as infrastructure endpoints rather than business functionality.
"""

import time

from flask import Flask, jsonify


def register_routes(app: Flask) -> None:
    """
    Register basic application routes to the Flask app.

    This function attaches routes like index and health check endpoints
    to the provided Flask application instance. These routes provide
    basic service information and health monitoring capabilities.

    Args:
        app (Flask): The Flask application instance to register routes with.
    """

    @app.route("/")
    def index():
        """
        Root endpoint that returns basic service information.

        Returns:
            Response: JSON containing service name, status, and version.
        """
        return jsonify(
            {
                "status": "ok",
                "service": "persona-engine",
                "version": app.config.get("VERSION", "0.1.0"),
            }
        )

    @app.route("/health")
    def health():
        """
        Health check endpoint for monitoring service health.

        This endpoint is typically used by load balancers, container orchestrators,
        or monitoring tools to determine if the service is operational.

        Returns:
            Response: JSON containing health status and current timestamp.
        """
        return jsonify({"status": "healthy", "timestamp": time.time()})
