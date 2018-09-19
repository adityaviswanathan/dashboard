#!/usr/bin/env python

'''
Builds a SQLAlchemy wrapper around the Flask app.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import os
import sys
from flask_sqlalchemy import SQLAlchemy
# Append parent dir to $PYTHONPATH to import Flask app.
my_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(my_path, os.pardir)))
from api import app

db = SQLAlchemy(app)
db.init_app(app)
