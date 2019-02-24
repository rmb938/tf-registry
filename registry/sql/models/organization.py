import uuid

from sqlalchemy import Column, String, func
from sqlalchemy_utils import ArrowType, UUIDType

from registry.sql.database import Base


class Organization(Base):
    __tablename__ = 'organizations'

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True, index=True)
    
    created_at = Column(ArrowType, index=True, nullable=False, server_default=func.now())
    updated_at = Column(ArrowType, nullable=False, server_default=func.now(), onupdate=func.now())
