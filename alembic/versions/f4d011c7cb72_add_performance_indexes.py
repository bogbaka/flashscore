from alembic import op


revision = "f4d011c7cb72"
down_revision = "82e5e25084cb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_matches_kickoff_at",
        "matches",
        ["kickoff_at"],
    )

    op.create_index(
        "ix_matches_status",
        "matches",
        ["status"],
    )

    op.create_index(
        "ix_matches_competition_id",
        "matches",
        ["competition_id"],
    )

    op.create_index(
        "ix_matches_home_team_id",
        "matches",
        ["home_team_id"],
    )

    op.create_index(
        "ix_matches_away_team_id",
        "matches",
        ["away_team_id"],
    )

    op.create_index(
        "ix_match_events_match_id",
        "match_events",
        ["match_id"],
    )

    op.create_index(
        "ix_standings_competition_id",
        "standings",
        ["competition_id"],
    )

    op.create_index(
        "ix_standings_team_id",
        "standings",
        ["team_id"],
    )

    op.create_index(
        "ix_favorites_user_id",
        "favorites",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_favorites_user_id",
        table_name="favorites",
    )

    op.drop_index(
        "ix_standings_team_id",
        table_name="standings",
    )

    op.drop_index(
        "ix_standings_competition_id",
        table_name="standings",
    )

    op.drop_index(
        "ix_match_events_match_id",
        table_name="match_events",
    )

    op.drop_index(
        "ix_matches_away_team_id",
        table_name="matches",
    )

    op.drop_index(
        "ix_matches_home_team_id",
        table_name="matches",
    )

    op.drop_index(
        "ix_matches_competition_id",
        table_name="matches",
    )

    op.drop_index(
        "ix_matches_status",
        table_name="matches",
    )

    op.drop_index(
        "ix_matches_kickoff_at",
        table_name="matches",
    )