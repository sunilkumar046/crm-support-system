"""add user role enum

Revision ID: e2bf4c337498
Revises: 987b7a6dcfbd
Create Date: 2026-08-29 10:08:34.731200

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2bf4c337498'
down_revision: Union[str, Sequence[str], None] = '987b7a6dcfbd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_role_enum = sa.Enum(
        "admin",
        "support_agent",
        "customer",
        name="userrole"
    )

    user_role_enum.create(op.get_bind(), checkfirst=True)

    op.alter_column(
        "users",
        "role",
        existing_type=sa.VARCHAR(length=30),
        type_=user_role_enum,
        existing_nullable=False,
        postgresql_using="role::text::userrole"
    )

def downgrade() -> None:
    op.alter_column(
        "users",
        "role",
        existing_type=sa.Enum(
            "admin",
            "support_agent",
            "customer",
            name="userrole"
        ),
        type_=sa.VARCHAR(length=30),
        existing_nullable=False
    )

    user_role_enum = sa.Enum(
        "admin",
        "support_agent",
        "customer",
        name="userrole"
    )

    user_role_enum.drop(op.get_bind(), checkfirst=True)