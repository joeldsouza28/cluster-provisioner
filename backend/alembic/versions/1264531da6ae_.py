"""empty message

Revision ID: 1264531da6ae
Revises: 243ae8c87d8c
Create Date: 2025-03-31 20:16:15.500694

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1264531da6ae'
down_revision: Union[str, None] = '243ae8c87d8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('gcp_remote_backend_config',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bucket_name', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_gcp_remote_backend_config_id'), 'gcp_remote_backend_config', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_gcp_remote_backend_config_id'), table_name='gcp_remote_backend_config')
    op.drop_table('gcp_remote_backend_config')
    # ### end Alembic commands ###
