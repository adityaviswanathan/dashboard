#!/usr/bin/env python

'''
Basic script to initialize database with some test entries.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import argparse
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--num_owners', type=int, default=1, help='number of owners to generate')
    parser.add_argument(
        '--num_properties', type=int, default=1, help='number of properties to generate per owner')
    parser.add_argument(
        '--num_managers', type=int, default=1, help='number of managers to generate per property')
    parser.add_argument(
        '--num_units', type=int, default=1, help='number of units to generate per property')
    parser.add_argument(
        '--num_tenants', type=int, default=1, help='number of tenants to generate per property')
    parser.add_argument(
        '--num_tickets', type=int, default=1, help='number of tickets to generate per tenant')
    parser.add_argument(
        '--num_contracts', type=int, default=1, help='number of contracts to generate per min(units, tenants)')
    parser.add_argument(
        '--num_transactions', type=int, default=0, help='number of transactions to generate per contract')
    args = parser.parse_args()
    migrate = Migrate(app, db)
    migrate.init_app(app)
    db.drop_all()
    db.create_all()
    make_entities(num_owners=args.num_owners,
                  num_properties=args.num_properties,
                  num_managers=args.num_managers,
                  num_units=args.num_units,
                  num_tenants=args.num_tenants,
                  num_tickets=args.num_tickets,
                  num_contracts=args.num_contracts,
                  num_transactions=args.num_transactions)
