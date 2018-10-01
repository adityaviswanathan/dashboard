#!/usr/bin/env python

'''
The entities in the app have has-many relationships in the following manner:
- Owner
-- Property <-> Bank account (payee)
--- Manager
--- Tenant <-> Bank account/cc (payer)
---- Ticket
--- Unit
---- Contract
- Contractor <-> Bank account (payee)
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

import datetime
import stripe
import time
from api import app
from db import db
from sqlalchemy import ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash


class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.BigInteger, primary_key=True)
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(
        db.DateTime, default=db.func.now(), onupdate=db.func.now())

    # Used for setting '_id' fields for models, ensuring the reference exists.
    def set_id(self, id_key, id_val, debug=False):
        class_name = id_key[0:id_key.find('_id')].capitalize()
        # Do not raise exception here because this method makes a best effort at
        # updating the referenced id column, skipping if not possible
        try:
            ref = eval(class_name).query_by_id(id_val)
            # Prevent an id ref from being set for a non-existent entity.
            if ref is None:
                if debug:
                    print 'Unable to overwrite field %s' % id_key
                return
        except:
            if debug:
                print 'Unable to overwrite field %s' % id_key
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

class User(Base):
    __abstract__ = True
    password_hash = db.Column(db.String(128))
    email = db.Column(db.Text)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Owner(User):
    __tablename__ = 'owner'
    properties = relationship('Property', backref='owner')

    @staticmethod
    def create(password, email):
        owner = Owner()
        owner.set_password(password)
        owner.email = email
        owner.save()
        return owner

    @staticmethod
    def dict_has_all_required_keys(data_dict):
        filtered_cols = []
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


class Property(Base):
    __tablename__ = 'property'
    address = db.Column(db.Text)
    owner_id = db.Column(db.Integer, ForeignKey('owner.id'))
    stripe_account_id = db.Column(db.Text)
    managers = relationship('Manager', backref='property')
    units = relationship('Unit', backref='property')

    @staticmethod
    def dict_has_all_required_keys(data_dict):
        filtered_cols = ['stripe_account_id']
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

    def create_payments(self, token, debug=False):
        if self.stripe_account_id is not None:
            raise Exception('Property %s already has an account id %s' %
                            (self.id, self.stripe_account_id))
        owner = Owner.query_by_id(self.owner_id)
        if debug:
            print 'Creating Stripe account for owner with email %s' % owner.email
        stripe_account = stripe.Account.create(
            type='custom', country='US', email=owner.email)
        stripe_account.legal_entity.type = 'individual'
        stripe_account.external_accounts.create(external_account=token)
        stripe_account.tos_acceptance.date = int(time.time())
        stripe_account.tos_acceptance.ip = '127.0.0.1'
        stripe_account.save()
        if debug:
            print 'Verified new Stripe account for property at address %s' % self.address
        self.stripe_account_id = stripe_account['id']

class Manager(User):
    __tablename__ = 'manager'
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
    def create(password, email, property_id):
        manager = Manager()
        manager.set_password(password)
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


class Tenant(User):
    __tablename__ = 'tenant'
    property_id = db.Column(db.Integer, ForeignKey('property.id'))
    stripe_account_id = db.Column(db.Text)
    tickets = relationship('Ticket', backref='tenant')

    @staticmethod
    def dict_has_all_required_keys(data_dict):
        all_filtered_cols = set(filtered_cols + Base.base_cols())
        tenant_cols = [
            col.name for col in Tenant.__table__.columns if col.name not in all_filtered_cols]
        return set(tenant_cols).issubset(set(data_dict.keys()))

    @staticmethod
    def create(password, email, property_id):
        tenant = Tenant()
        tenant.set_password(password)
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

    def create_payments(self, token, debug=False):
        if self.stripe_account_id is not None:
            raise Exception('Tenant %s already has an account id %s' %
                            (self.id, self.stripe_account_id))
        if debug:
            print 'Creating Stripe account for tenant with email %s' % self.email
        stripe_customer = stripe.Customer.create(
            email=self.email, source=token)
        stripe_bank_account = stripe_customer.sources.retrieve(stripe_customer.default_source)
        if debug:
            stripe_bank_account.verify(amounts=[32, 45])
            print 'Verified bank details for Tenant %s' % self.email
        # TODO(aditya): Prod bank acct verification. Using test values above.
        self.stripe_account_id = stripe_customer['id']


class Ticket(Base):
    __tablename__ = 'ticket'
    tenant_id = db.Column(db.Integer, ForeignKey('tenant.id'))
    contractor_id = db.Column(db.Integer, ForeignKey('contractor.id'))
    amount = db.Column(db.Integer)

    @staticmethod
    def dict_has_all_required_keys(data_dict):
        filtered_cols = []
        all_filtered_cols = set(filtered_cols + Base.base_cols())
        ticket_cols = [
            col.name for col in Ticket.__table__.columns if col.name not in all_filtered_cols]
        return set(ticket_cols).issubset(set(data_dict.keys()))

    @staticmethod
    def create(tenant_id, contractor_id, amount):
        ticket = Ticket()
        ticket.set_id('tenant_id', tenant_id)
        ticket.set_id('contractor_id', contractor_id)
        ticket.amount = amount
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

class TicketPayment(Base):
    __tablename__ = 'ticket_payment'
    ticket_id = db.Column(db.Integer, ForeignKey('ticket.id'))

    @staticmethod
    def to_cents(dollars):
        return dollars * 100

    @staticmethod
    def create(ticket_id, debug=True):
        ticket = Ticket.query_by_id(ticket_id)
        tenant = Tenant.query_by_id(ticket.tenant_id)
        prop = Property.query_by_id(tenant.property_id)
        contractor = Contractor.query_by_id(ticket.contractor_id)
        # Transfer amount from Property -> self.
        stripe_charge = stripe.Charge.create(
            amount=TicketPayment.to_cents(ticket.amount),
            currency='usd',
            source=prop.stripe_account_id,
            description='test charge'
        )
        if debug:
            print 'Created Stripe charge from Property %s to self' % prop.stripe_account_id
        # Transfer amount from self -> Contractor.
        stripe_charge = stripe.Transfer.create(
            amount=TicketPayment.to_cents(ticket.amount),
            currency='usd',
            source_transaction=stripe_charge['id'],
            destination=contractor.stripe_account_id,
            description='test charge'
        )
        if debug:
            print 'Created Stripe charge from self to Contractor %s' % contractor.stripe_account_id
        ticket_payment = TicketPayment()
        ticket_payment.ticket_id = ticket_id
        ticket_payment.save()
        return ticket_payment

    @staticmethod
    def query_by_id(in_id):
        if in_id is None:
            return None
        return TicketPayment.query.filter_by(id=in_id).first()

    @staticmethod
    def query_all():
        return TicketPayment.query.all()

    @staticmethod
    def query_by_ticket_id(ticket_id):
        if ticket_id is None:
            return None
        return TicketPayment.query.filter_by(ticket_id=ticket_id).all()


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
    rent = db.Column(db.Integer)

    @staticmethod
    def dict_has_all_required_keys(data_dict):
        filtered_cols = []
        all_filtered_cols = set(filtered_cols + Base.base_cols())
        contract_cols = [
            col.name for col in Contract.__table__.columns if col.name not in all_filtered_cols]
        return set(contract_cols).issubset(set(data_dict.keys()))

    @staticmethod
    def create(unit_id, tenant_id, rent):
        contract = Contract()
        contract.set_id('unit_id', unit_id)
        contract.set_id('tenant_id', tenant_id)
        contract.rent = rent
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


class ContractPayment(Base):
    __tablename__ = 'contract_payment'
    contract_id = db.Column(db.Integer, ForeignKey('contract.id'))

    @staticmethod
    def to_cents(dollars):
        return dollars * 100

    @staticmethod
    def create(contract_id, debug=True):
        contract = Contract.query_by_id(contract_id)
        unit = Unit.query_by_id(contract.unit_id)
        tenant = Tenant.query_by_id(contract.tenant_id)
        customer = stripe.Customer.retrieve(tenant.stripe_account_id)
        prop = Property.query_by_id(unit.property_id)
        # Transfer rent from Tenant -> Property.
        stripe_charge = stripe.Charge.create(
            amount=ContractPayment.to_cents(contract.rent),
            currency='usd',
            customer=customer['id'],
            destination=prop.stripe_account_id,
            description='test charge'
        )
        if debug:
            print 'Created Stripe charge from Tenant %s to Property %s' % (customer['id'], prop.stripe_account_id)
        contract_payment = ContractPayment()
        contract_payment.contract_id = contract_id
        contract_payment.save()
        return contract_payment

    @staticmethod
    def query_by_id(in_id):
        if in_id is None:
            return None
        return ContractPayment.query.filter_by(id=in_id).first()

    @staticmethod
    def query_all():
        return ContractPayment.query.all()

    @staticmethod
    def query_by_contract_id(contract_id):
        if contract_id is None:
            return None
        return ContractPayment.query.filter_by(contract_id=contract_id).all()

class Contractor(User):
    __tablename__ = 'contractor'
    stripe_account_id = db.Column(db.Text)
    tickets = relationship('Ticket', backref='contractor')

    @staticmethod
    def dict_has_all_required_keys(data_dict):
        filtered_cols = ['stripe_account_id']
        all_filtered_cols = set(filtered_cols + Base.base_cols())
        prop_cols = [
            col.name for col in Property.__table__.columns if col.name not in all_filtered_cols]
        return set(prop_cols).issubset(set(data_dict.keys()))

    @staticmethod
    def create(password, email):
        contractor = Contractor()
        contractor.set_password(password)
        contractor.email = email
        contractor.save()
        return contractor

    @staticmethod
    def query_by_id(in_id):
        if in_id is None:
            return None
        return Contractor.query.filter_by(id=in_id).first()

    @staticmethod
    def query_all():
        return Contractor.query.all()

    def create_payments(self, token, debug=False):
        if self.stripe_account_id is not None:
            raise Exception('Contractor %s already has an account id %s' %
                            (self.id, self.stripe_account_id))
        if debug:
            print 'Creating Stripe account for contractor with email %s' % self.email
        stripe_account = stripe.Account.create(
            type='custom', country='US', email=self.email)
        stripe_account.legal_entity.type = 'individual'
        stripe_account.external_accounts.create(external_account=token)
        stripe_account.tos_acceptance.date = int(time.time())
        stripe_account.tos_acceptance.ip = '127.0.0.1'
        stripe_account.save()
        if debug:
            print 'Verified new Stripe account for contractor with email %s' % self.email
        self.stripe_account_id = stripe_account['id']
