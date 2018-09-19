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
        entity_name = entity_str.capitalize()
        if entity_name == 'Owner':
            return Entity.OWNER
        if entity_name == 'Property':
            return Entity.PROPERTY
        if entity_name == 'Manager':
            return Entity.MANAGER
        if entity_name == 'Tenant':
            return Entity.TENANT
        if entity_name == 'Ticket':
            return Entity.TICKET
        if entity_name == 'Unit':
            return Entity.UNIT
        if entity_name == 'Contract':
            return Entity.CONTRACT
        raise Exception('Entity enum %s not recognized' % entity_name)

    @staticmethod
    def row2dict(r):
        row_dict = {}
        for c in r.__table__.columns:
            if getattr(r, c.name) is None:
                row_dict[c.name] = {'type': str(c.type)}
            else:
                row_dict[c.name] = {'data': str(getattr(r, c.name)),
                                    'type': str(c.type)}
        return row_dict

    @staticmethod
    def payment_params():
        return ['payment_name', 'payment_account_number', 'payment_routing_number']

    def __init__(self, entity_name):
        self.entity = ActionExecutor.string2entity(entity_name)

    def query_all(self):
        data = []
        if self.entity == Entity.OWNER:
            data = [ActionExecutor.row2dict(entry)
                    for entry in Owner.query_all()]
        if self.entity == Entity.PROPERTY:
            data = [ActionExecutor.row2dict(entry)
                    for entry in Property.query_all()]
        if self.entity == Entity.MANAGER:
            data = [ActionExecutor.row2dict(entry)
                    for entry in Manager.query_all()]
        if self.entity == Entity.TENANT:
            data = [ActionExecutor.row2dict(entry)
                    for entry in Tenant.query_all()]
        if self.entity == Entity.TICKET:
            data = [ActionExecutor.row2dict(entry)
                    for entry in Ticket.query_all()]
        if self.entity == Entity.UNIT:
            data = [ActionExecutor.row2dict(entry)
                    for entry in Unit.query_all()]
        if self.entity == Entity.CONTRACT:
            data = [ActionExecutor.row2dict(entry)
                    for entry in Contract.query_all()]
        return data

    def create(self, payload):
        entry = None
        if self.entity == Entity.OWNER:
            if not Owner.dict_has_all_required_keys(payload):
                raise Exception('Entity %s was not supplied a complete payload for construction' %
                                ActionExecutor.entity2string(self.entity))
            owner = Owner.create(**payload)
            entry = ActionExecutor.row2dict(owner)
        if self.entity == Entity.PROPERTY:
            if not Property.dict_has_all_required_keys(payload):
                raise Exception('Entity %s was not supplied a complete payload for construction' %
                                ActionExecutor.entity2string(self.entity))
            entry = ActionExecutor.row2dict(Property.create(**payload))
        if self.entity == Entity.MANAGER:
            if not Manager.dict_has_all_required_keys(payload):
                raise Exception('Entity %s was not supplied a complete payload for construction' %
                                ActionExecutor.entity2string(self.entity))
            entry = ActionExecutor.row2dict(Manager.create(**payload))
        if self.entity == Entity.TENANT:
            if not Tenant.dict_has_all_required_keys(payload):
                raise Exception('Entity %s was not supplied a complete payload for construction' %
                                ActionExecutor.entity2string(self.entity))
            tenant = Tenant.create(**payload)
            entry = ActionExecutor.row2dict(tenant)
        if self.entity == Entity.TICKET:
            if not Ticket.dict_has_all_required_keys(payload):
                raise Exception('Entity %s was not supplied a complete payload for construction' %
                                ActionExecutor.entity2string(self.entity))
            entry = ActionExecutor.row2dict(Ticket.create(**payload))
        if self.entity == Entity.UNIT:
            if not Unit.dict_has_all_required_keys(payload):
                raise Exception('Entity %s was not supplied a complete payload for construction' %
                                ActionExecutor.entity2string(self.entity))
            entry = ActionExecutor.row2dict(Unit.create(**payload))
        if self.entity == Entity.CONTRACT:
            if not Contract.dict_has_all_required_keys(payload):
                raise Exception('Entity %s was not supplied a complete payload for construction' %
                                ActionExecutor.entity2string(self.entity))
            entry = ActionExecutor.row2dict(Contract.create(**payload))
        if entry is None:
            raise Exception('Create semantics for %s are undefined' %
                            ActionExecutor.entity2string(self.entity))
        Db.session.commit()
        return entry

    def update(self, payload):
        entry = None
        if self.entity == Entity.OWNER:
            entry = Owner.query_by_id(payload['id'])
            if set(ActionExecutor.payment_params()).issubset(payload.keys()) and \
                all([payload[payment_param] for payment_param in ActionExecutor.payment_params()]):
                entry.create_payee(
                    payload['payment_name'], payload['payment_account_number'], payload['payment_routing_number'])
        if self.entity == Entity.PROPERTY:
            entry = Property.query_by_id(payload['id'])
        if self.entity == Entity.MANAGER:
            entry = Manager.query_by_id(payload['id'])
        if self.entity == Entity.TENANT:
            entry = Tenant.query_by_id(payload['id'])
            if set(ActionExecutor.payment_params()).issubset(payload.keys()) and \
                all([payload[payment_param] for payment_param in ActionExecutor.payment_params()]):
                entry.create_payer(
                    payload['payment_name'], payload['payment_account_number'], payload['payment_routing_number'])
        if self.entity == Entity.TICKET:
            entry = Ticket.query_by_id(payload['id'])
        if self.entity == Entity.UNIT:
            entry = Unit.query_by_id(payload['id'])
        if self.entity == Entity.CONTRACT:
            entry = Contract.query_by_id(payload['id'])
        if entry is None:
            raise Exception('Update semantics for %s are undefined' %
                            ActionExecutor.entity2string(self.entity))
        api_payload = {prop: payload[prop]
                       for prop in payload if prop not in ActionExecutor.payment_params()}
        entry.copy_from_dict(api_payload)
        Db.session.commit()
        return ActionExecutor.row2dict(entry)
