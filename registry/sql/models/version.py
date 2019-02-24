from sqlalchemy import Column, String, func, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy_utils import ArrowType

from registry.sql.database import Base, BigIntegerType


class Version(Base):
    __tablename__ = 'module_versions'

    id = Column(BigIntegerType, primary_key=True, autoincrement=True)
    module_id = Column(BigIntegerType, ForeignKey('modules.id'), nullable=False)
    provider = Column(String, nullable=False)
    version = Column(String, nullable=False)

    created_at = Column(ArrowType, index=True, nullable=False, server_default=func.now())
    updated_at = Column(ArrowType, nullable=False, server_default=func.now(), onupdate=func.now())

    module = relationship("Module")

    __table_args__ = (
        Index("module_id_provider_idx", module_id, provider, unique=True),
        Index("module_id_provider_version_idx", module_id, provider, version, unique=True),
    )
