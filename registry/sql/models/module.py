import uuid

from sqlalchemy import Column, String, func, Index, ForeignKey
from sqlalchemy_utils import ArrowType, UUIDType

from registry.sql.database import Base


class Module(Base):
    __tablename__ = 'modules'

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUIDType, ForeignKey('organizations.id'), nullable=False, index=True)
    name = Column(String, nullable=False)

    created_at = Column(ArrowType, index=True, nullable=False, server_default=func.now())
    updated_at = Column(ArrowType, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("organization_id_name_idx", organization_id, name, unique=True),
    )


class ModuleProvider(Base):
    __tablename__ = 'module_providers'

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    module_id = Column(UUIDType, ForeignKey('modules.id'), nullable=False, index=True)
    name = Column(String, nullable=False)

    created_at = Column(ArrowType, index=True, nullable=False, server_default=func.now())
    updated_at = Column(ArrowType, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("module_id_name_idx", module_id, name, unique=True),
    )


class ModuleProviderVersion(Base):
    __tablename__ = 'module_provider_versions'

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    provider_id = Column(UUIDType, ForeignKey('module_providers.id'), nullable=False, index=True)
    version = Column(String, nullable=False)

    created_at = Column(ArrowType, index=True, nullable=False, server_default=func.now())
    updated_at = Column(ArrowType, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("provider_id_version_idx", provider_id, version, unique=True),
    )
