from app.config import settings


def test_start_rush_returns_words_without_article(authenticated_client, sample_words):
    response = authenticated_client.post("/rush/start")

    assert response.status_code == 200
    data = response.json()
    assert "rush_id" in data
    assert len(data["words"]) == len(sample_words)
    for word in data["words"]:
        assert "article" not in word


def test_start_rush_fails_without_words(authenticated_client):
    response = authenticated_client.post("/rush/start")

    assert response.status_code == 400


def test_submit_correct_answer(authenticated_client, sample_words):
    start_response = authenticated_client.post("/rush/start")
    rush_id = start_response.json()["rush_id"]
    word = sample_words[0]  # Hund, der

    response = authenticated_client.post(
        "/rush/answer",
        json={"rush_id": rush_id, "word_id": word.id, "proposed_article": "der"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] is True
    assert data["correct_article"] == "der"


def test_submit_incorrect_answer(authenticated_client, sample_words):
    start_response = authenticated_client.post("/rush/start")
    rush_id = start_response.json()["rush_id"]
    word = sample_words[0]  # Hund, der

    response = authenticated_client.post(
        "/rush/answer",
        json={"rush_id": rush_id, "word_id": word.id, "proposed_article": "die"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] is False
    assert data["correct_article"] == "der"


def test_finish_rush_returns_score_and_missed_words(authenticated_client, sample_words):
    start_response = authenticated_client.post("/rush/start")
    rush_id = start_response.json()["rush_id"]

    # Une bonne réponse, une mauvaise
    authenticated_client.post(
        "/rush/answer",
        json={
            "rush_id": rush_id,
            "word_id": sample_words[0].id,
            "proposed_article": "der",
        },
    )
    authenticated_client.post(
        "/rush/answer",
        json={
            "rush_id": rush_id,
            "word_id": sample_words[1].id,
            "proposed_article": "der",
        },  # faux, c'est "die"
    )

    response = authenticated_client.post(f"/rush/{rush_id}/finish")

    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 1
    assert data["total_words"] == 2
    assert len(data["words_to_review"]) == 1
    assert data["words_to_review"][0]["word"] == "Katze"


def test_word_mastered_after_streak_threshold_reached(
    authenticated_client, sample_words
):
    """
    Vérifie qu'un mot devient maîtrisé après avoir été réussi sur
    MASTERY_STREAK_THRESHOLD rushs distincts, pas juste répondu N fois
    dans un seul rush.
    """

    word = sample_words[0]  # Hund, der

    for _ in range(settings.mastery_streak_threshold):
        start_response = authenticated_client.post("/rush/start")
        rush_id = start_response.json()["rush_id"]
        authenticated_client.post(
            "/rush/answer",
            json={"rush_id": rush_id, "word_id": word.id, "proposed_article": "der"},
        )
        authenticated_client.post(f"/rush/{rush_id}/finish")

    response = authenticated_client.get("/words?level=A1&status=mastered")
    data = response.json()

    mastered_ids = [w["id"] for w in data["words"]]
    assert word.id in mastered_ids


def test_word_unmastered_after_wrong_answer(authenticated_client, sample_words):
    """Un mot maîtrisé redevient non maîtrisé après une seule mauvaise réponse."""

    word = sample_words[0]  # Hund, der

    # Le maîtriser d'abord
    for _ in range(settings.mastery_streak_threshold):
        start_response = authenticated_client.post("/rush/start")
        rush_id = start_response.json()["rush_id"]
        authenticated_client.post(
            "/rush/answer",
            json={"rush_id": rush_id, "word_id": word.id, "proposed_article": "der"},
        )
        authenticated_client.post(f"/rush/{rush_id}/finish")

    # Puis se tromper une fois
    start_response = authenticated_client.post("/rush/start")
    rush_id = start_response.json()["rush_id"]
    authenticated_client.post(
        "/rush/answer",
        json={"rush_id": rush_id, "word_id": word.id, "proposed_article": "die"},
    )

    response = authenticated_client.get("/words?level=A1&status=mastered")
    data = response.json()

    mastered_ids = [w["id"] for w in data["words"]]
    assert word.id not in mastered_ids
