def test_register_creates_user_and_sends_otp(client, mock_send_otp_email):
    response = client.post(
        "/auth/register",
        json={
            "pseudo": "testuser",
            "email": "test@example.com",
            "password": "Test1234",
            "password_confirmation": "Test1234",
            "level": "A1",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["pseudo"] == "testuser"
    assert data["email_validated_at"] is None
    mock_send_otp_email.assert_called_once()


def test_register_rejects_duplicate_email(client, mock_send_otp_email):
    payload = {
        "pseudo": "testuser",
        "email": "test@example.com",
        "password": "Test1234",
        "password_confirmation": "Test1234",
        "level": "A1",
    }
    client.post("/auth/register", json=payload)

    payload["pseudo"] = "otheruser"
    response = client.post("/auth/register", json=payload)

    assert response.status_code == 400
    assert "déjà utilisée" in response.json()["detail"]


def test_login_blocked_before_email_validation(client, mock_send_otp_email):
    client.post(
        "/auth/register",
        json={
            "pseudo": "testuser",
            "email": "test@example.com",
            "password": "Test1234",
            "password_confirmation": "Test1234",
            "level": "A1",
        },
    )

    response = client.post(
        "/auth/login", json={"identifier": "testuser", "password": "Test1234"}
    )

    assert response.status_code == 401
    assert "valider" in response.json()["detail"]


def test_full_flow_register_verify_login(client, mock_send_otp_email, db_session):
    from app.models import User

    client.post(
        "/auth/register",
        json={
            "pseudo": "testuser",
            "email": "test@example.com",
            "password": "Test1234",
            "password_confirmation": "Test1234",
            "level": "A1",
        },
    )

    # On récupère l'OTP réellement généré en base (le mock a intercepté
    # l'envoi, mais pas la génération du code)
    user = db_session.query(User).filter(User.email == "test@example.com").first()
    otp_code = user.otp_code

    verify_response = client.post(
        "/auth/verify-otp", json={"email": "test@example.com", "otp_code": otp_code}
    )
    assert verify_response.status_code == 200
    assert verify_response.json()["email_validated_at"] is not None

    login_response = client.post(
        "/auth/login", json={"identifier": "testuser", "password": "Test1234"}
    )
    assert login_response.status_code == 200
    assert "session_token" in login_response.cookies


def test_register_rejects_short_password(client, mock_send_otp_email):
    response = client.post(
        "/auth/register",
        json={
            "pseudo": "testuser",
            "email": "test@example.com",
            "password": "short",
            "password_confirmation": "short",
            "level": "A1",
        },
    )

    assert response.status_code == 422


def test_register_rejects_invalid_level(client, mock_send_otp_email):
    response = client.post(
        "/auth/register",
        json={
            "pseudo": "testuser",
            "email": "test@example.com",
            "password": "Test1234",
            "password_confirmation": "Test1234",
            "level": "D3",
        },
    )

    assert response.status_code == 422
