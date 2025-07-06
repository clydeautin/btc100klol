"""adding daily_image_version

Revision ID: 3aab80a54bda
Revises: 3d5c42d3a6e7
Create Date: 2025-05-02 10:26:41.613205

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

prompt_type_enum = postgresql.ENUM(
    "GET_HOLIDAYS",
    "GENERATE_IMAGE_SAD",
    "GENERATE_IMAGE_HAPPY",
    name="prompttype",
    create_type=False,
)

task_status_enum = postgresql.ENUM(
    "PENDING", "PROCESSING", "COMPLETED", "FAILED", name="taskstatus", create_type=False
)


# revision identifiers, used by Alembic.
revision: str = "3aab80a54bda"
down_revision: Union[str, None] = "3d5c42d3a6e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # Create 'prompttype' enum if it doesn't exist
    bind.execute(
        text(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_type WHERE typname = 'prompttype'
                ) THEN
                    CREATE TYPE prompttype AS ENUM ('GET_HOLIDAYS', 'GENERATE_IMAGE_SAD', 'GENERATE_IMAGE_HAPPY');
                END IF;
            END
            $$;
            """
        )
    )

    # Create 'taskstatus' enum if it doesn't exist
    bind.execute(
        text(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_type WHERE typname = 'taskstatus'
                ) THEN
                    CREATE TYPE taskstatus AS ENUM ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED');
                END IF;
            END
            $$;
            """
        )
    )

    op.create_table(
        "daily_image_version",
        sa.Column("image_link_id", sa.Integer(), nullable=False),
        sa.Column("presigned_url", sa.Text(), nullable=True),
        sa.Column("presigned_url_expiry", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("prompt_type", prompt_type_enum, nullable=False),
        sa.Column("prompt_date", sa.Date(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("status", task_status_enum, server_default="PENDING", nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("created_ts", sa.Integer(), nullable=False),
        sa.Column("last_modified", sa.DateTime(), nullable=False),
        sa.Column("last_modified_ts", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["image_link_id"], ["image_link.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_daily_image_version_image_link_id"),
        "daily_image_version",
        ["image_link_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_daily_image_version_image_link_id"), table_name="daily_image_version"
    )
    op.drop_table("daily_image_version")

    # Do not drop enums shared across multiple tables (e.g., 'prompttype', 'taskstatus')
