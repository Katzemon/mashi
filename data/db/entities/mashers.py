from sqlalchemy import Column, BigInteger, String
from data.db.postgres_db import db


class Mashers(db.Base):
    __tablename__ = "mashers"
    userid = Column(BigInteger, primary_key=True, nullable=False)
    wallet = Column(String, nullable=True)
