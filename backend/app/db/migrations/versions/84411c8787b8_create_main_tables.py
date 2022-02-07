"""create_main_tables

Revision ID: 84411c8787b8
Revises: 
Create Date: 2022-01-18 02:23:18.434249
"""
from typing import Tuple

from alembic import op
import sqlalchemy as sa


revision = '84411c8787b8'
down_revision = None
branch_labels = None
depends_on = None


def create_updated_at_trigger() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS
        $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """
    )


def timestamps(indexed: bool = False) -> Tuple[sa.Column, sa.Column]:
    return (
        sa.Column(
            "created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False, index=indexed,
        ),
        sa.Column(
            "updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False, index=indexed,
        ),
    )


def create_users_table() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.Text, unique=True, nullable=False, index=True),
        sa.Column("email", sa.Text, unique=True, nullable=False, index=True),
        sa.Column("email_verified", sa.Boolean, nullable=False, server_default="False"),
        sa.Column("salt", sa.Text, nullable=False),
        sa.Column("password", sa.Text, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="True"),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default="False"),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_user_modtime
            BEFORE UPDATE
            ON users
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )


def create_profiles_table() -> None:
    op.create_table(
        "profiles",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("full_name", sa.Text, nullable=True),
        sa.Column("phone_number", sa.Text, nullable=True),
        sa.Column("bio", sa.Text, nullable=True, server_default=""),
        sa.Column("image", sa.Text, nullable=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_profiles_modtime
            BEFORE UPDATE
            ON profiles
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )


def create_cleanings_table() -> None:
    op.create_table(
        "cleanings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.Text, nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("cleaning_type", sa.Text, nullable=False, server_default="spot_clean"),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("owner", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_cleanings_modtime
            BEFORE UPDATE
            ON cleanings
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )


def create_offers_table() -> None:
    op.create_table(
        "user_offers_for_cleanings",
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "cleaning_id",
            sa.Integer,
            sa.ForeignKey("cleanings.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "status",
            sa.Text,
            nullable=False,
            server_default="pending",
            index=True
        ),
        *timestamps(),
    )
    op.create_primary_key("pk_user_offers_for_cleaning", "user_offers_for_cleanings", ["user_id", "cleaning_id"])
    op.execute(
        """
        CREATE TRIGGER update_user_offers_for_cleanings_modtime
            BEFORE UPDATE
            ON user_offers_for_cleanings
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )

def create_cleaner_evaluations_table() -> None:
    """
    Owner of a cleaning job should be able to evaluate cleaner's execution of the job.
    - Allow owner to leave ratings, headline, and comment.
    - Also add no show if the cleaner failed to show up.
    - Rating split into section:
        - professionalism - did they handle things like pros?
        - completeness - how thorough were they? did everything get cleaned as it should have?
        - efficiency - how quickly and effectively did they get the job done?
        - overall - what's the consensus rating for this cleaning job.
    """
    op.create_table(
        "cleaning_to_cleaner_evaluations",
        sa.Column(
            "cleaning_id",
            sa.Integer,
            sa.ForeignKey("cleanings.id", ondelete="SET NULL"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "cleaner_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=False,
            index=True
        ),
        sa.Column("no_show", sa.Boolean, nullable=False, server_default="False"),
        sa.Column("headline", sa.Text, nullable=True),
        sa.Column("comment", sa.Text, nullable=True),
        sa.Column("professionalism", sa.Integer, nullable=True),
        sa.Column("completeness", sa.Integer, nullable=True),
        sa.Column("efficiency", sa.Integer, nullable=True),
        sa.Column("overall_rating", sa.Integer, nullable=False),
        *timestamps()
    )

    op.create_primary_key(
        "pk_cleaning_to_cleaner_evaluations", "cleaning_to_cleaner_evaluations", ["cleaning_id", "cleaner_id"]
    )
    op.execute(
        """
        CREATE TRIGGER update_cleaning_to_cleaner_evaluations_modtime
            BEFORE UPDATE
            ON cleaning_to_cleaner_evaluations
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )


def upgrade() -> None:
    create_updated_at_trigger()
    create_users_table()
    create_profiles_table()
    create_cleanings_table()
    create_offers_table()
    create_cleaner_evaluations_table()


def downgrade() -> None:
    op.drop_table("cleaning_to_cleaner_evaluations")
    op.drop_table("user_offers_for_cleanings")
    op.drop_table("cleanings")
    op.drop_table("profiles")
    op.drop_table("users")
    op.execute("DROP FUNCTION update_updated_at_column")