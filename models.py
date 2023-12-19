#models.py
from sqlalchemy import Column, String, DateTime
from db import Base

class Email(Base):
    __tablename__ = 'emails'
    id = Column(String, primary_key=True)
    subject = Column(String)
    sender = Column(String)
    body = Column(String)
    received_at = Column(DateTime)