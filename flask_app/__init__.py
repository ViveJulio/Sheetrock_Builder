from flask import Flask
import os

app = Flask(__name__)

app.secret_key = os.environ.get("secret_key")