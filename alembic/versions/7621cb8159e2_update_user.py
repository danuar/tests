"""update_user

Revision ID: 7621cb8159e2
Revises: 830384bce001
Create Date: 2023-11-24 05:45:47.199731

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7621cb8159e2'
down_revision = '830384bce001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('results_tests', sa.Column('start_date', sa.DateTime(), nullable=False))
    op.alter_column('results_tests', 'completed_date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.add_column('users', sa.Column('ipAddress', sa.String(), nullable=False))
    op.add_column('users', sa.Column('userAgent', sa.String(), nullable=False))
    op.create_unique_constraint(None, 'users', ['userAgent'])
    op.create_unique_constraint(None, 'users', ['ipAddress'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_column('users', 'userAgent')
    op.drop_column('users', 'ipAddress')
    op.alter_column('results_tests', 'completed_date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.drop_column('results_tests', 'start_date')
    # ### end Alembic commands ###
