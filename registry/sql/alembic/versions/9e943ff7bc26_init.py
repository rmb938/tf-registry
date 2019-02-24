"""init

Revision ID: 9e943ff7bc26
Revises: 
Create Date: 2019-02-23 12:15:34.130811

"""
import sqlalchemy as sa
import sqlalchemy_utils as sa_utils
from alembic import op

# revision identifiers, used by Alembic.

revision = '9e943ff7bc26'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'organizations',
        sa.Column('id', sa_utils.UUIDType, primary_key=True),
        sa.Column('name', sa.String, nullable=False, unique=True, index=True),
        sa.Column('created_at', sa_utils.ArrowType, index=True, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa_utils.ArrowType, nullable=False, server_default=sa.func.now(),
                  onupdate=sa.func.now())
    )

    op.create_table(
        'modules',
        sa.Column('id', sa_utils.UUIDType, primary_key=True),
        sa.Column('organization_id', sa_utils.UUIDType, sa.ForeignKey('organizations.id'), nullable=False, index=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('created_at', sa_utils.ArrowType, index=True, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa_utils.ArrowType, nullable=False, server_default=sa.func.now(),
                  onupdate=sa.func.now())
    )
    op.create_index('organization_id_name_idx', 'modules', ['organization_id', 'name'], unique=True)

    op.create_table(
        'module_providers',
        sa.Column('id', sa_utils.UUIDType, primary_key=True),
        sa.Column('module_id', sa.String, sa.ForeignKey('modules.id'), nullable=False, index=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('created_at', sa_utils.ArrowType, index=True, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa_utils.ArrowType, nullable=False, server_default=sa.func.now(),
                  onupdate=sa.func.now())
    )
    op.create_index('module_id_name_idx', 'module_providers', ['module_id', 'name'], unique=True)

    op.create_table(
        'module_provider_versions',
        sa.Column('id', sa_utils.UUIDType, primary_key=True),
        sa.Column('provider_id', sa.String, sa.ForeignKey('module_providers.id'), nullable=False, index=True),
        sa.Column('version', sa.String, nullable=False),
        sa.Column('created_at', sa_utils.ArrowType, index=True, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa_utils.ArrowType, nullable=False, server_default=sa.func.now(),
                  onupdate=sa.func.now())
    )
    op.create_index('provider_id_version_idx', 'module_provider_versions', ['provider_id', 'version'], unique=True)


def downgrade():
    op.drop_index('module_id_name_idx', 'module_providers')
    op.drop_table('module_providers')
    op.drop_index('provider_id_version_idx', 'module_provider_versions')
    op.drop_table('module_provider_versions')
    op.drop_index('organization_id_name_idx', 'modules')
    op.drop_table('modules')
    op.drop_table('organizations')
