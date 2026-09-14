from tests.conftest import _master_word


def test_list_words_default_returns_all(authenticated_client, sample_words):
    response = authenticated_client.get("/words")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(sample_words)


def test_list_words_filtered_by_level(authenticated_client, sample_words):
    response = authenticated_client.get("/words?level=A1")

    assert response.status_code == 200
    data = response.json()
    assert all(w["level"] == "A1" for w in data["words"])


def test_list_words_filtered_by_not_started_status(authenticated_client, sample_words):
    word = sample_words[0]
    _master_word(authenticated_client, word)

    response = authenticated_client.get("/words?status=not_started")
    data = response.json()

    returned_ids = [w["id"] for w in data["words"]]
    assert word.id not in returned_ids
    assert data["total"] == len(sample_words) - 1


def test_list_words_pagination(authenticated_client, sample_words):
    response = authenticated_client.get("/words?page=1&page_size=2")
    data = response.json()

    assert len(data["words"]) == 2
    assert data["total"] == len(sample_words)
    assert data["page"] == 1
    assert data["page_size"] == 2


def test_list_words_requires_authentication(client):
    response = client.post("/rush/start")

    assert response.status_code == 401
