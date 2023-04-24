from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from database import Base

IMPORTANCE = ('Essential', 'Have to have', 'Nice to have', 'Should not have')

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), unique=True, index=True)
    username = Column(String(45), unique=True, index=True)
    first_name = Column(String(45), unique=True, index=True)
    last_name = Column(String(45), unique=True, index=True)
    hashed_password = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)

    accounts = relationship("Accounts", back_populates='owner', cascade='all,delete', passive_deletes=all)
    accounttypes = relationship("AccountTypes", back_populates='owner', cascade='all,delete', passive_deletes=all)
    incometypes = relationship("IncomeTypes", back_populates='owner', cascade='all,delete', passive_deletes=all)
    expensetypes = relationship("ExpenseTypes", back_populates='owner', cascade='all,delete', passive_deletes=all)

class Accounts(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(String(200))
    card_type = Column(Integer, ForeignKey('accounttypes.id'))
    balance = Column(Float)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))

    incomes = relationship('Incomes', back_populates='accountowner', cascade='all,delete', passive_deletes=all)
    expenses = relationship('Expenses', back_populates='accountowner', cascade='all,delete', passive_deletes=all)
    owner = relationship('Users', back_populates='accounts')


class Incomes(Base):
    __tablename__ = 'incomes'
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    t_type = Column(Integer, ForeignKey('incometypes.id'))
    description = Column(String(200))
    owner_id = Column(Integer, ForeignKey('users.id'))
    account_id = Column(Integer, ForeignKey('accounts.id', ondelete='CASCADE'))

    accountowner = relationship('Accounts', back_populates='incomes')

class Expenses(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    t_type = Column(Integer, ForeignKey('expensetypes.id'))
    description = Column(String(200))
    importance = Column(Enum('Essential', 'Have to have', 'Nice to have', 'Should not have', name='importance_enum'))
    owner_id = Column(Integer, ForeignKey('users.id'))
    account_id = Column(Integer, ForeignKey('accounts.id', ondelete='CASCADE'))

    accountowner = relationship('Accounts', back_populates='expenses')


class AccountTypes(Base):
    __tablename__ = 'accounttypes'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)
    owner_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))

    owner = relationship('Users', back_populates='accounttypes')


class IncomeTypes(Base):
    __tablename__ = 'incometypes'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)
    owner_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))

    owner = relationship('Users', back_populates='incometypes')


class ExpenseTypes(Base):
    __tablename__ = 'expensetypes'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)
    owner_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))

    owner = relationship('Users', back_populates='expensetypes')