from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), unique=True, index=True)
    username = Column(String(45), unique=True, index=True)
    first_name = Column(String(45), unique=True, index=True)
    last_name = Column(String(45), unique=True, index=True)
    hashed_password = Column(String(200))
    is_active = Column(Boolean, default=True)

    cards = relationship("Cards", back_populates='owner', cascade='all,delete', passive_deletes=all)

class Cards(Base):
    __tablename__ = 'cards'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(String(200))
    card_type = Column(Integer, ForeignKey('cardtypes.id'))
    balance = Column(Float)
    created_at = Column(DateTime)
    owner_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))

    
    incomes = relationship('Incomes', back_populates='cardowner', cascade='all,delete', passive_deletes=all)
    expenses = relationship('Expenses', back_populates='cardowner', cascade='all,delete', passive_deletes=all)
    owner = relationship('Users', back_populates='cards')

class Incomes(Base):
    __tablename__ = 'incomes'
    id = Column(Integer, primary_key=True, index=True)
    income_type = Column(Integer, ForeignKey('incometypes.id'))
    amount = Column(Float)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)
    card_id = Column(Integer, ForeignKey('cards.id', ondelete='CASCADE'))

    cardowner = relationship('Cards', back_populates='incomes')


class Expenses(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True, index=True)
    expense_type = Column(Integer, ForeignKey('expensetypes.id'))
    amount = Column(Float)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)
    card_id = Column(Integer, ForeignKey('cards.id', ondelete='CASCADE'))

    cardowner = relationship('Cards', back_populates='expenses')


class CardTypes(Base):
    __tablename__ = 'cardtypes'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(String(200))


class IncomeTypes(Base):
    __tablename__ = 'incometypes'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(String(200))


class ExpenseTypes(Base):
    __tablename__ = 'expensetypes'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(String(200))