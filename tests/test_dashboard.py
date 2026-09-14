from tests.conftest import _master_word


def test_dashboard_initial_state(authenticated_client, sample_words):
    response = authenticated_client.get("/users/me/dashboard")

    assert response.status_code == 200
    data = response.json()
    assert data["level"] == "A1"
    assert data["total_words"] == len(sample_words)
    assert data["mastered_words"] == 0
    assert data["not_started_words"] == len(sample_words)
    assert data["level_completed"] is False
    assert data["last_rush_score"] is None


def test_dashboard_reflects_mastered_word(authenticated_client, sample_words):
    word = sample_words[0]
    _master_word(authenticated_client, word)

    response = authenticated_client.get("/users/me/dashboard")
    data = response.json()

    assert data["mastered_words"] == 1
    assert data["not_started_words"] == len(sample_words) - 1


def test_dashboard_reflects_last_and_best_rush_score(
    authenticated_client, sample_words
):
    start_response = authenticated_client.post("/rush/start")
    rush_id = start_response.json()["rush_id"]
    authenticated_client.post(
        "/rush/answer",
        json={
            "rush_id": rush_id,
            "word_id": sample_words[0].id,
            "proposed_article": "der",
        },
    )
    authenticated_client.post(f"/rush/{rush_id}/finish")

    response = authenticated_client.get("/users/me/dashboard")
    data = response.json()

    assert data["last_rush_score"] == 1
    assert data["best_rush_score"] == 1
    assert data["total_rushes_played"] == 1


def test_advance_level_rejected_when_level_not_completed(
    authenticated_client, sample_words
):
    response = authenticated_client.post("/users/me/advance-level")

    assert response.status_code == 400
    assert "terminé" in response.json()["detail"]


def test_advance_level_succeeds_when_threshold_reached(
    authenticated_client, sample_words
):
    # Le seuil est bas (5 mots), on les maîtrise tous pour dépasser LEVEL_COMPLETION_THRESHOLD
    for word in sample_words:
        _master_word(authenticated_client, word)

    response = authenticated_client.post("/users/me/advance-level")

    assert response.status_code == 200
    assert response.json()["level"] == "A2"
