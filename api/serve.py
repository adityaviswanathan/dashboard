#!/usr/bin/env python
'''
Serves the HTTP interface to FormulaEngine via a REST API.
TODO(aditya): Define HTTP interface to FormulaEngine via a REST API.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello'

if __name__ == '__main__':
    app.run(debug=True)
