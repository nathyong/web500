"""Defines the Flask application itself for web500.
"""

from flask import Flask

app = Flask(__name__)

import web500.config
import web500.handlers
import web500.routes

app.config.from_object(web500.config)
