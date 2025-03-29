"""empty message

Revision ID: 88e6ae54e05a
Revises: 
Create Date: 2025-03-29 18:39:28.581268

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '88e6ae54e05a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('azure_keys',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_id', sa.String(), nullable=True),
    sa.Column('client_secret', sa.String(), nullable=True),
    sa.Column('tenant_id', sa.String(), nullable=True),
    sa.Column('subscription_id', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_azure_keys_id'), 'azure_keys', ['id'], unique=False)
    op.create_table('gcp_keys',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.String(), nullable=True),
    sa.Column('private_key_id', sa.String(), nullable=True),
    sa.Column('private_key', sa.String(), nullable=True),
    sa.Column('client_email', sa.String(), nullable=True),
    sa.Column('client_id', sa.String(), nullable=True),
    sa.Column('type', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_gcp_keys_id'), 'gcp_keys', ['id'], unique=False)
    op.create_index(op.f('ix_gcp_keys_project_id'), 'gcp_keys', ['project_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_gcp_keys_project_id'), table_name='gcp_keys')
    op.drop_index(op.f('ix_gcp_keys_id'), table_name='gcp_keys')
    op.drop_table('gcp_keys')
    op.drop_index(op.f('ix_azure_keys_id'), table_name='azure_keys')
    op.drop_table('azure_keys')
    # ### end Alembic commands ###
