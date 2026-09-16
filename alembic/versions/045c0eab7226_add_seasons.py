from alembic import op
import sqlalchemy as sa


revision = "48629c794b8d"
down_revision = "f4d011c7cb72"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "seasons",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),
        sa.Column(
            "competition_id",
            sa.Integer(),
            sa.ForeignKey("competitions.id"),
            nullable=False,
        ),
        sa.Column(
            "year",
            sa.Integer(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "competition_id",
            "year",
            name="uq_seasons_competition_year",
        ),
    )

    op.create_index(
        "ix_seasons_competition_id",
        "seasons",
        ["competition_id"],
    )

    op.add_column(
        "matches",
        sa.Column(
            "season_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "standings",
        sa.Column(
            "season_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_matches_season_id",
        "matches",
        "seasons",
        ["season_id"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_standings_season_id",
        "standings",
        "seasons",
        ["season_id"],
        ["id"],
    )

    op.create_index(
        "ix_matches_season_id",
        "matches",
        ["season_id"],
    )

    op.create_index(
        "ix_standings_season_id",
        "standings",
        ["season_id"],
    )

    op.execute(
        """
        INSERT INTO seasons (competition_id, year)
        SELECT competition_id, 2024
        FROM (
            SELECT DISTINCT competition_id
            FROM matches

            UNION

            SELECT DISTINCT competition_id
            FROM standings
        ) AS existing_competitions
        """
    )

    op.execute(
        """
        UPDATE matches
        SET season_id = seasons.id
        FROM seasons
        WHERE seasons.competition_id = matches.competition_id
          AND seasons.year = 2024
        """
    )

    op.execute(
        """
        UPDATE standings
        SET season_id = seasons.id
        FROM seasons
        WHERE seasons.competition_id = standings.competition_id
          AND seasons.year = 2024
        """
    )

    op.alter_column(
        "matches",
        "season_id",
        nullable=False,
    )

    op.alter_column(
        "standings",
        "season_id",
        nullable=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_standings_season_id",
        table_name="standings",
    )

    op.drop_index(
        "ix_matches_season_id",
        table_name="matches",
    )

    op.drop_constraint(
        "fk_standings_season_id",
        "standings",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_matches_season_id",
        "matches",
        type_="foreignkey",
    )

    op.drop_column(
        "standings",
        "season_id",
    )

    op.drop_column(
        "matches",
        "season_id",
    )

    op.drop_index(
        "ix_seasons_competition_id",
        table_name="seasons",
    )

    op.drop_table("seasons")