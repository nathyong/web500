"""Defines the Flask application itself for web500.
"""

from flask import Flask

import web500.config
import web500.routes

app = Flask(__name__)

app.config.from_object(web500.config)
