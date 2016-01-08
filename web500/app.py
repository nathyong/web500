"""Defines the Flask application itself for web500.
"""

from flask import Flask
from web500.gen_css import convert_dir
from os.path import dirname, join

app = Flask(__name__)

#convert all scss files in scss/ folder to css
cd = dirname(__file__) #current directory
convert_dir(join(cd, 'scss'), join(cd, 'static/css/gen'))

import web500.config
import web500.routes

app.config.from_object(web500.config)
