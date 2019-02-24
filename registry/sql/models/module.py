from sqlalchemy import Column, String, func, Index, ForeignKey
from sqlalchemy_utils import ArrowType

from registry.sql.database import Base, BigIntegerType


class Module(Base):
    __tablename__ = 'modules'

    id = Column(BigIntegerType, primary_key=True, autoincrement=True)
    organization_id = Column(BigIntegerType, ForeignKey('organizations.id'), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(ArrowType, index=True, nullable=False, server_default=func.now())
    updated_at = Column(ArrowType, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("organization_name_idx", organization_id, name, unique=True),
    )
