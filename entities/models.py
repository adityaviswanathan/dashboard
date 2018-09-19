#!/usr/bin/env python

'''
The entities in the app have has-many relationships in the following manner:
- Owner <-> Bank account (payee)
-- Property
--- Manager
--- Tenant <-> Bank account/cc (payer)
---- Ticket
--- Unit
---- Contract
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import datetime
import stripe
from api import app
from db import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.BigInteger, primary_key=True)
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(
        db.DateTime, default=db.func.now(), onupdate=db.func.now())

    # Used for setting '_id' fields for models, ensuring the reference exists.
    def set_id(self, id_key, id_val):
        class_name = id_key[0:id_key.find('_id')].capitalize()
        try:
            ref = eval(class_name).query_by_id(id_val)
            # Prevent an id ref from being set for a non-existent entity.
            if ref is None:
                return
        except:
            return
        setattr(self, id_key, id_val)

    @staticmethod
    def base_cols():
        return ['id', 'created_on', 'updated_on']

    # Copies as much data from data_dict as possible besides Base model fields
    # id, created_on, updated_on.
    def copy_from_dict(self, data_dict):
        filtered_cols = Base.base_cols()
        all_cols = [col.name for col in self.__table__.columns]
        for key, value in data_dict.iteritems():
            if key in filtered_cols:
                continue
            if key not in all_cols:
                raise Exception(
                    'Cannot copy value %s because %s is not a valid column' % (value, key))
            if key.endswith('id'):
                self.set_id(key, value)
            else:
                setattr(self, key, value)

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
    stripe_account_id = db.Column(db.Text)
    stripe_bank_account_id = db.Column(db.Text)
    properties = relationship('Property', backref='owner')

    @staticmethod
    def create(email):
        owner = Owner()
        owner.email = email
        owner.save()
        return owner

    @staticmethod
    def dict_has_all_required_keys(data_dict):
        filtered_cols = ['stripe_account_id', 'stripe_bank_account_id']
        all_filtered_cols = set(filtered_cols + Base.base_cols())
        owner_cols = [
            col.name for col in Owner.__table__.columns if col.name not in all_filtered_cols]
        return set(owner_cols).issubset(set(data_dict.keys()))

    @staticmethod
    def query_by_id(in_id):
        if in_id is None:
            return None
        return Owner.query.filter_by(id=in_id).first()

    @staticmethod
    def query_all():
        return Owner.query.all()

    def create_payee(self, payee_name, account_number, routing_number):
        if self.stripe_account_id is not None:
            raise Exception('Owner %s already has an account id %s' %
                            (self.id, self.stripe_account_id))
        if self.stripe_bank_account_id is not None:
            raise Exception('Owner %s already has an bank account id %s' %
                            (self.id, self.stripe_bank_account_id))
        print 'Creating Stripe account for owner with email %s' % self.email
        account_res = stripe.Account.create(
            type='custom', country='US', email=self.email)
        self.stripe_account_id = account_res['id']
        stripe_account = stripe.Account.retrieve(self.stripe_account_id)
        print 'Creating Stripe bank account for owner with name %s' % payee_name
        bank_res = stripe_account.external_accounts.create(external_account={
            'object': 'bank_account',
            'country': 'US',
            'currency': 'usd',
            'account_holder_name': payee_name,
            'account_holder_type': 'individual',
            'routing_number': app.config.get('STRIPE_TEST_ROUTING_NUMBER', routing_number),
            'account_number': app.config.get('STRIPE_TEST_ACCOUNT_NUMBER', account_number)
        })
        self.stripe_bank_account_id = bank_res['id']


class Property(Base):
    __tablename__ = 'property'
    address = db.Column(db.Text)
    owner_id = db.Column(db.Integer, ForeignKey('owner.id'))
    managers = relationship('Manager', backref='property')
    units = relationship('Unit', backref='property')

    def __init__(self):
        self.required_columns = ['email']

    @staticmethod
    def dict_has_all_required_keys(data_dict):
        filtered_cols = []
        all_filtered_cols = set(filtered_cols + Base.base_cols())
        prop_cols = [
            col.name for col in Property.__table__.columns if col.name not in all_filtered_cols]
        return set(prop_cols).issubset(set(data_dict.keys()))

    @staticmethod
    def create(address, owner_id):
        prop = Property()
        prop.address = address
        prop.set_id('owner_id', owner_id)
        prop.save()
        return prop

    @staticmethod
    def query_by_id(in_id):
        if in_id is None:
            return None
        return Property.query.filter_by(id=in_id).first()

    @staticmethod
    def query_all():
        return Property.query.all()

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
    def dict_has_all_required_keys(data_dict):
        filtered_cols = []
        all_filtered_cols = set(filtered_cols + Base.base_cols())
        manager_cols = [
            col.name for col in Manager.__table__.columns if col.name not in all_filtered_cols]
        return set(manager_cols).issubset(set(data_dict.keys()))

    @staticmethod
    def create(email, property_id):
        manager = Manager()
        manager.email = email
        manager.set_id('property_id', property_id)
        manager.save()
        return manager

    @staticmethod
    def query_by_id(in_id):
        if in_id is None:
            return None
        return Manager.query.filter_by(id=in_id).first()

    @staticmethod
    def query_all():
        return Manager.query.all()

    @staticmethod
    def query_by_property_id(property_id):
        if property_id is None:
            return None
        return Manager.query.filter_by(property_id=property_id).all()


class Tenant(Base):
    __tablename__ = 'tenant'
    email = db.Column(db.Text)
    property_id = db.Column(db.Integer, ForeignKey('property.id'))
    stripe_account_id = db.Column(db.Text)
    stripe_bank_account_id = db.Column(db.Text)
    tickets = relationship('Ticket', backref='tenant')

    @staticmethod
    def dict_has_all_required_keys(data_dict):
        filtered_cols = ['stripe_account_id', 'stripe_bank_account_id']
        all_filtered_cols = set(filtered_cols + Base.base_cols())
        tenant_cols = [
            col.name for col in Tenant.__table__.columns if col.name not in all_filtered_cols]
        return set(tenant_cols).issubset(set(data_dict.keys()))

    @staticmethod
    def create(email, property_id):
        tenant = Tenant()
        tenant.email = email
        tenant.set_id('property_id', property_id)
        tenant.save()
        return tenant

    @staticmethod
    def query_by_id(in_id):
        if in_id is None:
            return None
        return Tenant.query.filter_by(id=in_id).first()

    @staticmethod
    def query_all():
        return Tenant.query.all()

    @staticmethod
    def query_by_property_id(property_id):
        if property_id is None:
            return None
        return Tenant.query.filter_by(property_id=property_id).all()

    def create_payer(self, payer_name, account_number, routing_number):
        if self.stripe_account_id.isnot(None):
            raise Exception('Tenant %s already has an account id %s' %
                            (self.id, self.stripe_account_id))
        if self.stripe_bank_account_id.isnot(None):
            raise Exception('Tenant %s already has an bank account id %s' %
                            (self.id, self.stripe_bank_account_id))
        print 'Creating Stripe account for tenant with email %s' % self.email
        customer_res = stripe.Customer.create(email=self.email)
        self.stripe_account_id = customer_res['id']
        stripe_account = stripe.Customer.retrieve(self.stripe_account_id)
        print 'Creating Stripe bank account for tenant with name %s' % payer_name
        bank_res = stripe_account.sources.create(source={
            'object': 'bank_account',
            'country': 'US',
            'currency': 'usd',
            'account_holder_name': payer_name,
            'account_holder_type': 'individual',
            'routing_number': app.config.get('STRIPE_TEST_ROUTING_NUMBER', routing_number),
            'account_number': app.config.get('STRIPE_TEST_ACCOUNT_NUMBER', account_number)
        })
        self.stripe_bank_account_id = bank_res['id']


class Ticket(Base):
    __tablename__ = 'ticket'
    tenant_id = db.Column(db.Integer, ForeignKey('tenant.id'))

    @staticmethod
    def dict_has_all_required_keys(data_dict):
        filtered_cols = []
        all_filtered_cols = set(filtered_cols + Base.base_cols())
        ticket_cols = [
            col.name for col in Ticket.__table__.columns if col.name not in all_filtered_cols]
        return set(ticket_cols).issubset(set(data_dict.keys()))

    @staticmethod
    def create(tenant_id):
        ticket = Ticket()
        ticket.set_id('tenant_id', tenant_id)
        ticket.save()
        return ticket

    @staticmethod
    def query_by_id(in_id):
        if in_id is None:
            return None
        return Ticket.query.filter_by(id=in_id).first()

    @staticmethod
    def query_all():
        return Ticket.query.all()

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
    def dict_has_all_required_keys(data_dict):
        filtered_cols = []
        all_filtered_cols = set(filtered_cols + Base.base_cols())
        unit_cols = [
            col.name for col in Unit.__table__.columns if col.name not in all_filtered_cols]
        return set(unit_cols).issubset(set(data_dict.keys()))

    @staticmethod
    def create(property_id):
        unit = Unit()
        unit.set_id('property_id', property_id)
        unit.save()
        return unit

    @staticmethod
    def query_by_id(in_id):
        if in_id is None:
            return None
        return Unit.query.filter_by(id=in_id).first()

    @staticmethod
    def query_all():
        return Unit.query.all()

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
    def dict_has_all_required_keys(data_dict):
        filtered_cols = []
        all_filtered_cols = set(filtered_cols + Base.base_cols())
        contract_cols = [
            col.name for col in Contract.__table__.columns if col.name not in all_filtered_cols]
        return set(contract_cols).issubset(set(data_dict.keys()))

    @staticmethod
    def create(unit_id, tenant_id):
        contract = Contract()
        contract.set_id('unit_id', unit_id)
        contract.set_id('tenant_id', tenant_id)
        contract.save()
        return contract

    @staticmethod
    def query_by_id(in_id):
        if in_id is None:
            return None
        return Contract.query.filter_by(id=in_id).first()

    @staticmethod
    def query_all():
        return Contract.query.all()

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

    def create_transaction(self):
        DUMMY_PAYMOUNT_AMOUNT = 100
        unit = Unit.query_by_id(unit_id)
        tenant = Tenant.query_by_id(tenant_id)
        # Charge the tenant for the payment
        customer = stripe.Customer.retrieve(tenant.stripe_account_id)
        bank_account = customer.sources.retrieve(tenant.stripe_bank_account_id)
        charge_res = stripe.Charge.create(
            amount=DUMMY_PAYMOUNT_AMOUNT,
            currency='usd',
            source=bank_account,
            description='test charge'
        )
        # TODO(aditya): Verify charge success
        # Transfer the payment from internal account to owner
        prop = Property.query_by_id(unit.property_id)
        owner = Owner.query_by_id(prop.owner_id)
        transfer_res = stripe.Transfer.create(
            amount=DUMMY_PAYMOUNT_AMOUNT,
            currency='usd',
            destination=owner.stripe_bank_account_id
        )
        # TODO(aditya): Verify transfer success
        print transfer_res
