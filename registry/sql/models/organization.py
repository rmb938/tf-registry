from sqlalchemy import Column, String, func
from sqlalchemy_utils import ArrowType

from registry.sql.database import Base, BigIntegerType


class Organization(Base):
    __tablename__ = 'organizations'

    id = Column(BigIntegerType, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(ArrowType, index=True, nullable=False, server_default=func.now())
    updated_at = Column(ArrowType, nullable=False, server_default=func.now(), onupdate=func.now())
