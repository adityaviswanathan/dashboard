#!/usr/bin/env python
'''
Tests entity wrapper over DB. We should be able to perform all CRUD operations
on all entity types.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import os
import sys
import unittest
from sqlalchemy import create_engine
from db import db
from models import *
# Append parent dir to $PYTHONPATH to import Flask app.
my_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(my_path, os.pardir)))
from api import app

class CanQueryAllEntities(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # Create database.
        # TODO(aditya): Be more careful here with dropping/initializing
        # database. Obviously we should never do this with prod resources, but
        # we might also want to separate dev resources from test resources.
        start_engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI_START'])
        with start_engine.begin() as start_cxn:
            start_cxn.execute('COMMIT')
            start_cxn.execute('DROP DATABASE IF EXISTS %s' % app.config['DATABASE_NAME'])
            start_cxn.execute('COMMIT')
            start_cxn.execute('CREATE DATABASE %s' % app.config['DATABASE_NAME'])
        start_engine.dispose()
        # Apply schema to new database.
        db.create_all()
        # Insert dummy records. We'll maintain a separate map of all records
        # from which we can ensure queries can reach all.
        dummystr = 'dummy'
        self.db_map = {
            'owners' : [],
            'properties' : [],
            'managers' : [],
            'tenants' : [],
            'tickets' : [],
            'units' : [],
            'contracts' : []
        }
        row2dict = lambda r: { c.name: str(getattr(r, c.name)) for c in r.__table__.columns }
        def make_owner(email):
            owner = Owner.create(email)
            db.session.commit()
            self.db_map['owners'].append(row2dict(owner))
            return owner
        def make_property(address, owner_id):
            prop = Property.create(address, owner_id)
            db.session.commit()
            self.db_map['properties'].append(row2dict(prop))
            return prop
        def make_manager(email, property_id):
            manager = Manager.create(email, property_id)
            db.session.commit()
            self.db_map['managers'].append(row2dict(manager))
            return manager
        def make_tenant(email, property_id):
            tenant = Tenant.create(email, property_id)
            db.session.commit()
            self.db_map['tenants'].append(row2dict(tenant))
            return tenant
        def make_ticket(tenant_id):
            ticket = Ticket.create(tenant_id)
            db.session.commit()
            self.db_map['tickets'].append(row2dict(ticket))
            return ticket
        def make_unit(property_id):
            unit = Unit.create(property_id)
            db.session.commit()
            self.db_map['units'].append(row2dict(unit))
            return unit
        def make_contract(unit_id, tenant_id):
            contract = Contract.create(unit_id, tenant_id)
            db.session.commit()
            self.db_map['contracts'].append(row2dict(contract))
            return contract
        # Inserts entries according to the supplied arguments.
        # NOTE: num_* args are not absolute counts of the number of each entity.
        # Rather, they are the count of each entity with respect to a single
        # parent. For example, if num_owners=2 and num_properties=2, there would
        # be a total of 2 owners and 4 properties in the database because each
        # owner has many properties.
        def make_entities(num_owners=1, num_properties=1, num_managers=1,
                          num_units=1, num_tenants=1, num_contracts=1,
                          num_tickets=1):
            if num_contracts > num_units:
                raise Exception('Cannot make %d contracts for %d units' % (num_contracts, num_units))
            if num_contracts > num_tenants:
                raise Exception('Cannot make %d contracts for %d tenants' % (num_contracts, num_tenants))
            for i in range(num_owners):
                owner = make_owner(dummystr)
                for i in range(num_properties):
                    prop = make_property(dummystr, owner.id)
                    for i in range(num_managers):
                        manager = make_manager(dummystr, prop.id)
                    unit_ids = []
                    tenant_ids = []
                    for i in range(num_units):
                        unit = make_unit(prop.id)
                        unit_ids.append(unit.id)
                    for i in range(num_tenants):
                        tenant = make_tenant(dummystr, prop.id)
                        tenant_ids.append(tenant.id)
                        for i in range(num_tickets):
                            ticket = make_ticket(tenant.id)
                    for i in range(num_contracts):
                        contract = make_contract(unit_ids[i], tenant_ids[i])
        make_entities(num_owners=2, num_properties=3, num_managers=5,
                      num_units=5, num_tenants=5, num_contracts=5,
                      num_tickets=5)

    def test_can_query_all(self):
        owners = Owner.query_all()
        removeById = lambda needle, haystack: [i for i in haystack if i['id'] != str(needle)]
        # Use query API to reach all inserted entities and prune from @self.db_map.
        for owner in owners:
            self.db_map['owners'] = removeById(owner.id, self.db_map['owners'])
            props = Property.query_by_owner_id(owner.id)
            for prop in props:
                self.db_map['properties'] = removeById(prop.id, self.db_map['properties'])
                managers = Manager.query_by_property_id(prop.id)
                for manager in managers:
                    self.db_map['managers'] = removeById(manager.id, self.db_map['managers'])
                tenants = Tenant.query_by_property_id(prop.id)
                for tenant in tenants:
                    self.db_map['tenants'] = removeById(tenant.id, self.db_map['tenants'])
                    tickets = Ticket.query_by_tenant_id(tenant.id)
                    for ticket in tickets:
                        self.db_map['tickets'] = removeById(ticket.id, self.db_map['tickets'])
                units = Unit.query_by_property_id(prop.id)
                for unit in units:
                    self.db_map['units'] = removeById(unit.id, self.db_map['units'])
                    contracts = Contract.query_by_unit_id(unit.id)
                    for contract in contracts:
                        self.db_map['contracts'] = removeById(contract.id, self.db_map['contracts'])
        # Assert that each record for each entity type has been reached via query API.
        self.assertEqual(len(self.db_map['owners']), 0)
        self.assertEqual(len(self.db_map['properties']), 0)
        self.assertEqual(len(self.db_map['managers']), 0)
        self.assertEqual(len(self.db_map['tenants']), 0)
        self.assertEqual(len(self.db_map['tickets']), 0)
        self.assertEqual(len(self.db_map['units']), 0)
        self.assertEqual(len(self.db_map['contracts']), 0)

if __name__ == '__main__':
    unittest.main()
