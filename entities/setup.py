#!/usr/bin/env python

'''
Basic script to initialize database with some test entries.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import os
import sys
from db import db
from flask_script import Manager as ScriptRunner
from flask_migrate import Migrate, MigrateCommand
from models import *
from test_entities import make_entities
# Append parent dir to $PYTHONPATH to import Flask app.
my_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(my_path, os.pardir)))
from api import app

migrate = Migrate(app, db)
migrate.init_app(app)
db.drop_all()
db.create_all()
make_entities(num_owners=2, num_properties=2, num_managers=2,
              num_units=2, num_tenants=2, num_contracts=2, num_tickets=2)
