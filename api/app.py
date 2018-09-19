#!/usr/bin/env python

'''
Serves the HTTP interface to FormulaEngine via a REST API.
TODO(aditya): Define HTTP interface to FormulaEngine via a REST API.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import os
import stripe
import sys
from flask import Flask
# Append parent dir to $PYTHONPATH to import ReportTraverser, whose public
# methods have bindings into Function.
my_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(my_path, os.pardir)))

UPLOAD_FOLDER = 'in'
app = Flask(__name__)
app.config.from_object('api.config.DevelopmentConfig')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
stripe.api_key = app.config['STRIPE_SECRET_KEY']
