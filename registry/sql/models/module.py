import uuid

from sqlalchemy import Column, String, func, Index, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils import ArrowType, UUIDType

from registry.sql.database import Base


class Module(Base):
    __tablename__ = 'modules'

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUIDType, ForeignKey('organizations.id'), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(ArrowType, index=True, nullable=False, server_default=func.now())
    updated_at = Column(ArrowType, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("organization_id_name_idx", organization_id, name, unique=True),
    )


class ModuleVersion(Base):
    __tablename__ = 'module_versions'

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    module_id = Column(UUIDType, ForeignKey('modules.id'), nullable=False)
    provider = Column(String, nullable=False)
    version = Column(String, nullable=False)

    created_at = Column(ArrowType, index=True, nullable=False, server_default=func.now())
    updated_at = Column(ArrowType, nullable=False, server_default=func.now(), onupdate=func.now())

    module = relationship("Module")

    __table_args__ = (
        Index("module_id_provider_idx", module_id, provider, unique=True),
        Index("module_id_provider_version_idx", module_id, provider, version, unique=True),
    )
