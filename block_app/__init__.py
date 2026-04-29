from flask import Flask, jsonify;
from block_app.routes.views import views

def make_blockway():
    block_app = Flask(__name__)
    block_app.register_blueprint(views)
    return block_app