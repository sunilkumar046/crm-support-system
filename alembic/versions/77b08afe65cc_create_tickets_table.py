"""create tickets table

Revision ID: 77b08afe65cc
Revises: b7034aa67604
Create Date: 2026-08-29 10:32:15.566379

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '77b08afe65cc'
down_revision: Union[str, Sequence[str], None] = 'b7034aa67604'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    ticket_priority = sa.Enum(
        'low',
        'medium',
        'high',
        'critical',
        name='ticketpriority'
    )

    ticket_status = sa.Enum(
        'open',
        'in_progress',
        'waiting_for_customer',
        'resolved',
        'closed',
        'cancelled',
        name='ticketstatus'
    )

    op.create_table(
        'tickets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),

        sa.Column(
            'priority',
            ticket_priority,
            nullable=False
        ),

        sa.Column(
            'status',
            ticket_status,
            nullable=False
        ),

        sa.Column(
            'assigned_agent_id',
            sa.Integer(),
            nullable=True
        ),

        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=True
        ),

        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=True
        ),

        sa.Column(
            'resolved_at',
            sa.DateTime(timezone=True),
            nullable=True
        ),

        sa.ForeignKeyConstraint(
            ['assigned_agent_id'],
            ['users.id']
        ),

        sa.ForeignKeyConstraint(
            ['category_id'],
            ['categories.id']
        ),

        sa.ForeignKeyConstraint(
            ['customer_id'],
            ['customers.id']
        ),

        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_tickets_assigned_agent_id'),
        'tickets',
        ['assigned_agent_id'],
        unique=False
    )

    op.create_index(
        op.f('ix_tickets_category_id'),
        'tickets',
        ['category_id'],
        unique=False
    )

    op.create_index(
        op.f('ix_tickets_customer_id'),
        'tickets',
        ['customer_id'],
        unique=False
    )

    op.create_index(
        op.f('ix_tickets_id'),
        'tickets',
        ['id'],
        unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:

    op.drop_index(
        op.f('ix_tickets_id'),
        table_name='tickets'
    )

    op.drop_index(
        op.f('ix_tickets_customer_id'),
        table_name='tickets'
    )

    op.drop_index(
        op.f('ix_tickets_category_id'),
        table_name='tickets'
    )

    op.drop_index(
        op.f('ix_tickets_assigned_agent_id'),
        table_name='tickets'
    )

    op.drop_table('tickets')

    ticket_status = sa.Enum(
        'open',
        'in_progress',
        'waiting_for_customer',
        'resolved',
        'closed',
        'cancelled',
        name='ticketstatus'
    )

    ticket_priority = sa.Enum(
        'low',
        'medium',
        'high',
        'critical',
        name='ticketpriority'
    )

    ticket_status.drop(
        op.get_bind(),
        checkfirst=True
    )

    ticket_priority.drop(
        op.get_bind(),
        checkfirst=True
    )