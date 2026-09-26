from unittest.mock import Mock

from app.integrations.football_api.client import FootballAPIClient
from app.services.competition_sync import CompetitionSyncService
from app.services.football_sync import FootballSyncService
from app.services.live_match import LiveMatchService
from app.services.live_worker import LiveSyncWorker
from app.services.match_event_sync import MatchEventSyncService
from app.services.match_sync import MatchSyncService
from app.services.standing_sync import StandingSyncService
from app.services.team_sync import TeamSyncService


def test_team_sync_does_not_close_shared_client(db_session):
    client = Mock(spec=FootballAPIClient)

    service = TeamSyncService(
        db_session,
        client=client,
    )

    service.close()

    client.close.assert_not_called()


def test_match_sync_does_not_close_shared_client(db_session):
    client = Mock(spec=FootballAPIClient)

    service = MatchSyncService(
        db_session,
        client=client,
    )

    service.close()

    client.close.assert_not_called()


def test_match_event_sync_does_not_close_shared_client(
    db_session,
):
    client = Mock(spec=FootballAPIClient)

    service = MatchEventSyncService(
        db_session,
        client=client,
    )

    service.close()

    client.close.assert_not_called()


def test_standing_sync_does_not_close_shared_client(
    db_session,
):
    client = Mock(spec=FootballAPIClient)

    service = StandingSyncService(
        db_session,
        client=client,
    )

    service.close()

    client.close.assert_not_called()


def test_competition_sync_does_not_close_shared_client(
    db_session,
):
    client = Mock(spec=FootballAPIClient)

    service = CompetitionSyncService(
        db_session,
        football_api=client,
    )

    service.close()

    client.close.assert_not_called()


def test_live_match_passes_shared_client_to_event_sync(
    db_session,
):
    client = Mock(spec=FootballAPIClient)

    service = LiveMatchService(
        db_session,
        client=client,
    )

    assert service.client is client
    assert service.event_sync.client is client

    service.close()

    client.close.assert_not_called()


def test_football_sync_shares_one_client(db_session):
    client = Mock(spec=FootballAPIClient)

    service = FootballSyncService(
        db_session,
        client=client,
    )

    assert service.client is client
    assert service.competition_sync.football_api is client
    assert service.team_sync.client is client
    assert service.match_sync.client is client
    assert service.match_event_sync.client is client
    assert service.standing_sync.client is client

    service.close()

    client.close.assert_not_called()


def test_live_worker_does_not_close_shared_client():
    client = Mock(spec=FootballAPIClient)

    worker = LiveSyncWorker(
        client=client,
    )

    worker.close()

    client.close.assert_not_called()


def test_live_worker_owns_created_client():
    worker = LiveSyncWorker()

    try:
        assert worker._owns_client is True
    finally:
        worker.close()


def test_live_worker_refreshes_final_match_events(
    db_session,
    monkeypatch,
):
    client = Mock(spec=FootballAPIClient)

    worker = LiveSyncWorker(
        client=client,
    )

    live_match = Mock()
    live_match.provider_id = 1037956
    live_match.status = "2H"

    refreshed_match = Mock()
    refreshed_match.provider_id = 1037956
    refreshed_match.status = "FT"

    mock_service = Mock()
    mock_service.refresh_score.return_value = refreshed_match

    monkeypatch.setattr(
        "app.services.live_worker.LiveMatchService",
        lambda **kwargs: mock_service,
    )

    monkeypatch.setattr(
        worker,
        "get_live_matches",
        lambda db: [live_match],
    )

    worker.run_once()

    mock_service.refresh_score.assert_called_once_with(
        1037956
    )

    mock_service.refresh_events.assert_called_once_with(
        1037956
    )

    worker.close()

    client.close.assert_not_called()
