from sqlalchemy import Float, Column

from .base import Base


class BitcoinPrice(Base):
  __tablename__ = 'bitcoin_prices'
  
  price = Column(Float, nullable=False)
