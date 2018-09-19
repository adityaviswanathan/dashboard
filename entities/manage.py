#!/usr/bin/env python

'''
DB migrations script.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import os
import sys
from flask_script import Manager as ScriptRunner
from flask_migrate import Migrate, MigrateCommand
from models import *
# Append parent dir to $PYTHONPATH to import Flask app.
my_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(my_path, os.pardir)))
from api import app
from db import db

migrate = Migrate(app, db)
manager = ScriptRunner(app)
# Sets 'db' as symbol for command-line invocation of migrations
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
