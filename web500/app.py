from flask import Flask, render_template
import web500.config

app = Flask(__name__)
app.settings = web500.config.settings


@app.route('/')
def index():
    """Handles the index page"""
    return render_template("index.html")
