#!/usr/bin/env python
'''
Tests entity wrapper over DB. We should be able to perform all CRUD operations
on all entity types.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import copy
import os
import string
import stripe
import sys
import random
import unittest
from sqlalchemy import create_engine
from db import db
from models import *
# Append parent dir to $PYTHONPATH to import Flask app.
my_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(my_path, os.pardir)))
from api import app

def lROW2DICT(r): return {c.name: str(getattr(r, c.name))
                          for c in r.__table__.columns}

# Inserts entries according to the supplied arguments.
# NOTE: num_* args are not absolute counts of the number of each entity.
# Rather, they are the count of each entity with respect to a single
# parent. For example, if num_owners=2 and num_properties=2, there would
# be a total of 2 owners and 4 properties in the database because each
# owner has many properties.
def make_entities(num_owners=1, num_properties=1, num_managers=1,
                  num_units=1, num_tenants=1, num_tickets=1, num_contracts=1,
                  num_transactions=1):
    stripe.api_key = app.config['STRIPE_SECRET_KEY']
    if num_contracts > num_units:
        raise Exception('Cannot make %d contracts for %d units' %
                        (num_contracts, num_units))
    if num_contracts > num_tenants:
        raise Exception('Cannot make %d contracts for %d tenants' %
                        (num_contracts, num_tenants))
    db_map = {
        'owners': [],
        'properties': [],
        'managers': [],
        'tenants': [],
        'tickets': [],
        'units': [],
        'contracts': [],
        'transactions': []
    }
    for i in range(num_owners):
        owner = Owner.create(app.config['DB_TEST_EMAIL'])
        owner.create_payee(app.config['DB_TEST_NAME'],
                           app.config['STRIPE_TEST_ACCOUNT_NUMBER'],
                           app.config['STRIPE_TEST_ROUTING_NUMBER'])
        db.session.commit()
        db_map['owners'].append(lROW2DICT(owner))
        for i in range(num_properties):
            prop = Property.create(app.config['DB_TEST_ADDRESS'], owner.id)
            db.session.commit()
            db_map['properties'].append(lROW2DICT(prop))
            for j in range(num_managers):
                manager = Manager.create(app.config['DB_TEST_EMAIL'], prop.id)
                db.session.commit()
                db_map['managers'].append(lROW2DICT(manager))
            unit_ids = []
            tenant_ids = []
            for k in range(num_units):
                unit = Unit.create(prop.id)
                db.session.commit()
                db_map['units'].append(lROW2DICT(unit))
                unit_ids.append(unit.id)
            for l in range(num_tenants):
                tenant = Tenant.create(app.config['DB_TEST_EMAIL'], prop.id)
                tenant.create_payer(app.config['DB_TEST_NAME'],
                                    app.config['STRIPE_TEST_ACCOUNT_NUMBER'],
                                    app.config['STRIPE_TEST_ROUTING_NUMBER'])
                db.session.commit()
                db_map['tenants'].append(lROW2DICT(tenant))
                tenant_ids.append(tenant.id)
                for m in range(num_tickets):
                    ticket = Ticket.create(tenant.id)
                    db.session.commit()
                    db_map['tickets'].append(lROW2DICT(ticket))
            for n in range(num_contracts):
                contract = Contract.create(unit_ids[k], tenant_ids[l], app.config['DB_TEST_AMOUNT'])
                db.session.commit()
                db_map['contracts'].append(lROW2DICT(contract))
                unit = Unit.query_by_id(unit_ids[k])
                prop = Property.query_by_id(unit.property_id)
                owner = Owner.query_by_id(prop.owner_id)
                tenant = Tenant.query_by_id(tenant_ids[l])
                for o in range(num_transactions):
                    transaction = Transaction.create(contract.id)
                    db.session.commit()
                    db_map['transactions'].append(lROW2DICT(transaction))
    return db_map


def makeTestDatabase(num_owners=1, num_properties=1, num_managers=1,
                     num_units=1, num_tenants=1, num_tickets=1,
                     num_contracts=1, num_transactions=1):
    # Apply schema to new database.
    db.drop_all()
    db.create_all()
    db.session.commit()
    # Insert dummy records. We'll maintain a separate map of all records
    # from which we can ensure queries can reach all.
    return make_entities(num_owners=num_owners, num_properties=num_properties, num_managers=num_managers,
                         num_units=num_units, num_tenants=num_tenants, num_tickets=num_tickets,
                         num_contracts=num_contracts, num_transactions=num_transactions)

def destroyTestDatabase():
    db.session.commit()
    db.drop_all()

# Walks schema hierarchy from top-most query, returning dictionary repr of db.
def databaseReachAll():
    owners = Owner.query_all()
    output_obj_dict = {'owners': [],
                       'properties': [],
                       'managers': [],
                       'tenants': [],
                       'tickets': [],
                       'units': [],
                       'contracts': [],
                       'transactions': []}
    for owner in owners:
        output_obj_dict['owners'].append(lROW2DICT(owner))
        props = Property.query_by_owner_id(owner.id)
        for prop in props:
            output_obj_dict['properties'].append(lROW2DICT(prop))
            managers = Manager.query_by_property_id(prop.id)
            for manager in managers:
                output_obj_dict['managers'].append(lROW2DICT(manager))
            tenants = Tenant.query_by_property_id(prop.id)
            for tenant in tenants:
                output_obj_dict['tenants'].append(lROW2DICT(tenant))
                tickets = Ticket.query_by_tenant_id(tenant.id)
                for ticket in tickets:
                    output_obj_dict['tickets'].append(lROW2DICT(ticket))
            units = Unit.query_by_property_id(prop.id)
            for unit in units:
                output_obj_dict['units'].append(lROW2DICT(unit))
                contracts = Contract.query_by_unit_id(unit.id)
                for contract in contracts:
                    output_obj_dict['contracts'].append(lROW2DICT(contract))
                    transactions = Transaction.query_by_contract_id(contract.id)
                    for transaction in transactions:
                        output_obj_dict['transactions'].append(lROW2DICT(transaction))
    return output_obj_dict



class CanQueryAllEntities(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.db = makeTestDatabase(num_owners=2, num_properties=2, num_managers=3,
                                   num_units=9, num_tenants=5, num_tickets=3,
                                   num_contracts=5, num_transactions=0)

    @classmethod
    def tearDownClass(self):
        destroyTestDatabase()

    def test_can_query_all(self):
        # Use query API to reach all inserted entities and prune from @self.db.
        reach_all_db = databaseReachAll()
        # Assert that each record for each entity type has been reached via query API.
        self.assertEqual(len(self.db['owners']), len(reach_all_db['owners']))
        self.assertListEqual(self.db['owners'], reach_all_db['owners'])
        self.assertEqual(len(self.db['properties']), len(reach_all_db['properties']))
        self.assertListEqual(self.db['properties'], reach_all_db['properties'])
        self.assertEqual(len(self.db['managers']), len(reach_all_db['managers']))
        self.assertListEqual(self.db['managers'], reach_all_db['managers'])
        self.assertEqual(len(self.db['tenants']), len(reach_all_db['tenants']))
        self.assertListEqual(self.db['tenants'], reach_all_db['tenants'])
        self.assertEqual(len(self.db['tickets']), len(reach_all_db['tickets']))
        self.assertListEqual(self.db['tickets'], reach_all_db['tickets'])
        self.assertEqual(len(self.db['units']), len(reach_all_db['units']))
        self.assertListEqual(self.db['units'], reach_all_db['units'])
        self.assertEqual(len(self.db['contracts']), len(reach_all_db['contracts']))
        self.assertListEqual(self.db['contracts'], reach_all_db['contracts'])
        self.assertEqual(len(self.db['transactions']), len(reach_all_db['transactions']))
        self.assertListEqual(self.db['transactions'], reach_all_db['transactions'])

class CanUpdateAllEntities(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        makeTestDatabase(num_owners=2, num_properties=2, num_managers=3,
                         num_units=9, num_tenants=5, num_tickets=3,
                         num_contracts=5, num_transactions=0)

    @classmethod
    def tearDownClass(self):
        destroyTestDatabase()

    def test_update_query_all(self):
        update_db = {'owners': [],
                     'properties': [],
                     'managers': [],
                     'tenants': [],
                     'tickets': [],
                     'units': [],
                     'contracts': [],
                     'transactions': []}
        def perturb(input_obj_dict):
            output_obj_dict = copy.deepcopy(input_obj_dict)
            filtered_cols = ['created_on', 'updated_on', 'rent']
            for key in input_obj_dict.keys():
                if not key.endswith('id') and key not in filtered_cols:
                    output_obj_dict[key] = ''.join(random.choice(
                        string.ascii_uppercase + string.digits) for _ in range(10))
            return output_obj_dict
        owners = Owner.query_all()
        # Use query API to update all inserted entities.
        for owner in owners:
            new_owner = perturb(lROW2DICT(owner))
            owner.copy_from_dict(new_owner)
            update_db['owners'].append(new_owner)
            props = Property.query_by_owner_id(owner.id)
            for prop in props:
                new_prop = perturb(lROW2DICT(prop))
                prop.copy_from_dict(new_prop)
                update_db['properties'].append(new_prop)
                managers = Manager.query_by_property_id(prop.id)
                for manager in managers:
                    new_manager = perturb(lROW2DICT(manager))
                    manager.copy_from_dict(new_manager)
                    update_db['managers'].append(new_manager)
                tenants = Tenant.query_by_property_id(prop.id)
                for tenant in tenants:
                    new_tenant = perturb(lROW2DICT(tenant))
                    tenant.copy_from_dict(new_tenant)
                    update_db['tenants'].append(new_tenant)
                    tickets = Ticket.query_by_tenant_id(tenant.id)
                    for ticket in tickets:
                        new_ticket = perturb(lROW2DICT(ticket))
                        ticket.copy_from_dict(new_ticket)
                        update_db['tickets'].append(new_ticket)
                units = Unit.query_by_property_id(prop.id)
                for unit in units:
                    new_unit = perturb(lROW2DICT(unit))
                    unit.copy_from_dict(new_unit)
                    update_db['units'].append(new_unit)
                    contracts = Contract.query_by_unit_id(unit.id)
                    for contract in contracts:
                        new_contract = perturb(lROW2DICT(contract))
                        contract.copy_from_dict(new_contract)
                        update_db['contracts'].append(new_contract)
                        transactions = Transaction.query_by_contract_id(contract.id)
                        for transaction in transactions:
                            new_transaction = perturb(lROW2DICT(transaction))
                            transaction.copy_from_dict(new_transaction)
                            update_db['transaction'].append(new_transaction)
        db.session.commit()
        # Ignore @filter_keys when making assertions (e.g. "updated_on" timestamp).
        def remove_inner_keys(input_dict, filter_keys=['updated_on']):
            updated_data_dict = {}
            for outerkey in input_dict.keys():
                if outerkey not in updated_data_dict:
                    updated_data_dict[outerkey] = []
                for inner_dict in input_dict[outerkey]:
                    data_dict = {}
                    for innerkey, val in inner_dict.iteritems():
                        if innerkey not in filter_keys:
                            data_dict[innerkey] = val
                updated_data_dict[outerkey].append(data_dict)
            return updated_data_dict
        reach_all_db = databaseReachAll()
        found_data_dict = remove_inner_keys(reach_all_db)
        updated_data_dict = remove_inner_keys(update_db)
        # Assert that each record for each entity type has been updated via query API.
        self.assertEqual(len(update_db['owners']), len(reach_all_db['owners']))
        self.assertListEqual(updated_data_dict['owners'], found_data_dict['owners'])
        self.assertEqual(len(update_db['properties']), len(reach_all_db['properties']))
        self.assertListEqual(updated_data_dict['properties'], found_data_dict['properties'])
        self.assertEqual(len(update_db['managers']), len(reach_all_db['managers']))
        self.assertListEqual(updated_data_dict['managers'], found_data_dict['managers'])
        self.assertEqual(len(update_db['tenants']), len(reach_all_db['tenants']))
        self.assertListEqual(updated_data_dict['tenants'], found_data_dict['tenants'])
        self.assertEqual(len(update_db['tickets']), len(reach_all_db['tickets']))
        self.assertListEqual(updated_data_dict['tickets'], found_data_dict['tickets'])
        self.assertEqual(len(update_db['units']), len(reach_all_db['units']))
        self.assertListEqual(updated_data_dict['units'], found_data_dict['units'])
        self.assertEqual(len(update_db['contracts']), len(reach_all_db['contracts']))
        self.assertListEqual(updated_data_dict['contracts'], found_data_dict['contracts'])
        self.assertEqual(len(update_db['transactions']), len(reach_all_db['transactions']))
        self.assertListEqual(updated_data_dict['transactions'], found_data_dict['transactions'])

# TODO(aditya): Add test for PUT ops via copy_from_dict().
if __name__ == '__main__':
    unittest.main()
