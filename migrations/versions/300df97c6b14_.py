"""empty message

Revision ID: 300df97c6b14
Revises: 2fdd3454780a
Create Date: 2022-07-01 11:47:09.125050

"""
from alembic import op
import sqlalchemy as sa

from api import SQL_INIT_FILE
from extras import get_inserts_from_files


# revision identifiers, used by Alembic.
revision = '300df97c6b14'
down_revision = '2fdd3454780a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    halls_table = op.create_table('halls',
    sa.Column('IDHall', sa.Integer(), nullable=False),
    sa.Column('HallNumber', sa.SmallInteger(), nullable=True),
    sa.Column('HallSquare', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('Windows', sa.SmallInteger(), nullable=False),
    sa.Column('Heaters', sa.SmallInteger(), nullable=False),
    sa.Column('TargetID', sa.Integer(), nullable=True),
    sa.Column('DepartmentID', sa.Integer(), nullable=True),
    sa.Column('KadastrID', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['DepartmentID'], ['departments.IDDepartment'], onupdate='CASCADE', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['KadastrID'], ['buildings.IDKadastr'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['TargetID'], ['targets.IDTarget'], onupdate='CASCADE', ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('IDHall')
    )
    # ### end Alembic commands ###
    inserts = get_inserts_from_files(SQL_INIT_FILE)
    op.bulk_insert(
        halls_table,
        inserts[halls_table.name]
    )


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('halls')
    # ### end Alembic commands ###