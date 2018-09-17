#!/usr/bin/env python

'''
Wrapper over models.py that enables generic constructor/query interface.
TODO(aditya): define business logic actions e.g. contract.charge_rent().
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import enum
from entities import Owner, Property, Manager, Tenant, Ticket, Unit, Contract, Db

class Entity(enum.Enum):
    OWNER = 0
    PROPERTY = 1
    MANAGER = 2
    TENANT = 3
    TICKET = 4
    UNIT = 5
    CONTRACT = 6

class ActionExecutor(object):
    @staticmethod
    def entity2string(entity_enum):
        if entity_enum is Entity.OWNER:
            return 'Owner'
        if entity_enum is Entity.PROPERTY:
            return 'Property'
        if entity_enum is Entity.MANAGER:
            return 'Manager'
        if entity_enum is Entity.TENANT:
            return 'Tenant'
        if entity_enum is Entity.TICKET:
            return 'Ticket'
        if entity_enum is Entity.UNIT:
            return 'Unit'
        if entity_enum is Entity.CONTRACT:
            return 'Contract'
        raise Exception('Entity enum %s not recognized' % entity_enum)

    @staticmethod
    def string2entity(entity_str):
        if entity_str == 'Owner':
            return Entity.OWNER
        if entity_str == 'Property':
            return Entity.PROPERTY
        if entity_str == 'Manager':
            return Entity.MANAGER
        if entity_str == 'Tenant':
            return Entity.TENANT
        if entity_str == 'Ticket':
            return Entity.TICKET
        if entity_str == 'Unit':
            return Entity.UNIT
        if entity_str == 'Contract':
            return Entity.CONTRACT
        raise Exception('Entity enum %s not recognized' % entity_str)

    @staticmethod
    def row2dict(r): return {c.name: {'data': str(getattr(r, c.name)), 'type': str(c.type)}
                             for c in r.__table__.columns}

    def __init__(self, entity_name):
        self.entity = ActionExecutor.string2entity(entity_name.capitalize())

    def is_payee(self):
        return self.entity in [Entity.OWNER]

    def is_payer(self):
        return self.entity in [Entity.TENANT]

    def query_all(self):
        data = [ActionExecutor.row2dict(entry) for entry in getattr(
            eval(ActionExecutor.entity2string(self.entity)), 'query_all')()]
        return data

    def create(self, payload):
        is_valid = getattr(eval(ActionExecutor.entity2string(
            self.entity)), 'dict_has_all_required_keys')(payload)
        if not is_valid:
            raise Exception('Entity %s was not supplied a complete payload for construction' %
                            ActionExecutor.entity2string(self.entity))
        entry = ActionExecutor.row2dict(getattr(
            eval(ActionExecutor.entity2string(self.entity)), 'create')(**payload))
        Db.session.commit()
        return entry

    def update(self, payload):
        entry = getattr(eval(ActionExecutor.entity2string(
            self.entity)), 'query_by_id')(payload['id'])
        getattr(entry, 'copy_from_dict')(payload)
        Db.session.commit()
        return ActionExecutor.row2dict(entry)

    def create_payee(self):
        if not self.is_payee():
            raise Exception('Entity %s cannot be a payee' %
                            ActionExecutor.entity2string(self.entity))
        # TODO(aditya): Setup Stripe account for payee.
