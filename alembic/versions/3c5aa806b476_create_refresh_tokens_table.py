"""create refresh_tokens table

Revision ID: 3c5aa806b476
Revises: 
Create Date: 2026-01-07 21:50:48.797572

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '3c5aa806b476'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'),  nullable=False),
        sa.Column('token_hash', sa.String, nullable=False),
        sa.Column('issued_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(index_name='ix_refresh_tokens_user_id', table_name='refresh_tokens', columns=['user_id'])
    op.create_index(index_name='ix_refresh_tokens_token_hash', table_name='refresh_tokens', columns=['token_hash'])
    op.create_index('uq_refresh_tokens_token_hash', table_name='refresh_tokens', columns=['token_hash'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_refresh_tokens_token_hash', table_name='refresh_tokens')
    op.drop_index('ix_refresh_tokens_user_id', table_name='refresh_tokens')
    op.drop_index('uq_refresh_tokens_token_hash', table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
