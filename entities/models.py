#!/usr/bin/env python

'''
The entities in the app have has-many relationships in the following manner:
- Owner
-- Property
--- Manager
--- Tenant
---- Ticket
--- Unit
---- Contract
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import datetime
from db import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.BigInteger, primary_key=True)
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def save(self):
        self.updated_on = datetime.datetime.utcnow()
        db.session.add(self)

    def delete(self):
        db.session.delete(self)

    def __repr__(self):
        return '<%s %d>' % (self.__class__.__name__, self.id)

class Owner(Base):
    __tablename__ = 'owner'
    email = db.Column(db.Text)
    properties = relationship('Property', backref='owner')

    @staticmethod
    def create(email):
        owner = Owner()
        owner.email = email
        owner.save()
        return owner

    @staticmethod
    def query_all():
        return Owner.query.all()

class Property(Base):
    __tablename__ = 'property'
    address = db.Column(db.Text)
    owner_id = db.Column(db.Integer, ForeignKey('owner.id'))
    managers = relationship('Manager', backref='property')
    units = relationship('Unit', backref='property')

    @staticmethod
    def create(address, owner_id):
        prop = Property()
        prop.address = address
        prop.owner_id = owner_id
        prop.save()
        return prop

    @staticmethod
    def query_by_owner_id(owner_id):
        if owner_id is None:
            return None
        return Property.query.filter_by(owner_id=owner_id).all()

class Manager(Base):
    __tablename__ = 'manager'
    email = db.Column(db.Text)
    # Assuming a manager runs at most one property.
    property_id = db.Column(db.Integer, ForeignKey('property.id'))

    @staticmethod
    def create(email, property_id):
        manager = Manager()
        manager.email = email
        manager.property_id = property_id
        manager.save()
        return manager

    @staticmethod
    def query_by_property_id(property_id):
        if property_id is None:
            return None
        return Manager.query.filter_by(property_id=property_id).all()

class Tenant(Base):
    __tablename__ = 'tenant'
    email = db.Column(db.Text)
    property_id = db.Column(db.Integer, ForeignKey('property.id'))
    tickets = relationship('Ticket', backref='tenant')

    @staticmethod
    def create(email, property_id):
        tenant = Tenant()
        tenant.email = email
        tenant.property_id = property_id
        tenant.save()
        return tenant

    @staticmethod
    def query_by_property_id(property_id):
        if property_id is None:
            return None
        return Tenant.query.filter_by(property_id=property_id).all()

class Ticket(Base):
    __tablename__ = 'ticket'
    tenant_id = db.Column(db.Integer, ForeignKey('tenant.id'))

    @staticmethod
    def create(tenant_id):
        ticket = Ticket()
        ticket.tenant_id = tenant_id
        ticket.save()
        return ticket

    @staticmethod
    def query_by_tenant_id(tenant_id):
        if tenant_id is None:
            return None
        return Ticket.query.filter_by(tenant_id=tenant_id).all()

class Unit(Base):
    __tablename__ = 'unit'
    property_id = db.Column(db.Integer, ForeignKey('property.id'))
    contracts = relationship('Contract', backref='unit')

    @staticmethod
    def create(property_id):
        unit = Unit()
        unit.property_id = property_id
        unit.save()
        return unit

    @staticmethod
    def query_by_property_id(property_id):
        if property_id is None:
            return None
        return Unit.query.filter_by(property_id=property_id).all()

class Contract(Base):
    __tablename__ = 'contract'
    unit_id = db.Column(db.Integer, ForeignKey('unit.id'))
    tenant_id = db.Column(db.Integer, ForeignKey('tenant.id'))

    @staticmethod
    def create(unit_id, tenant_id):
        contract = Contract()
        contract.unit_id = unit_id
        contract.tenant_id = tenant_id
        contract.save()
        return contract

    @staticmethod
    def query_by_unit_id(unit_id):
        if unit_id is None:
            return None
        return Contract.query.filter_by(unit_id=unit_id).all()

    @staticmethod
    def query_by_tenant_id(tenant_id):
        if tenant_id is None:
            return None
        return Contract.query.filter_by(tenant_id=tenant_id).all()


