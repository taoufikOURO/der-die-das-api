import requests

from app.config import settings


def send_otp_email(to_email: str, otp_code: str) -> None:
    """
    Envoie un code de sécurité par email via l'API Brevo.
    Ce code peut être utilisé pour la validation de l'adresse
    email ou la réinitialisation du mot de passe.
    """

    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": settings.brevo_api_key,
        "content-type": "application/json",
    }

    text_body = (
        f"Votre code de sécurité est : {otp_code}\n\n"
        f"Ce code est valable {settings.otp_expiry_minutes} minutes.\n\n"
        "Si vous n'êtes pas à l'origine de cette demande, "
        "vous pouvez ignorer cet email."
    )

    html_body = f"""
    <html>
      <body>
        <h2>Votre code de sécurité</h2>

        <p>Voici votre code de sécurité :</p>

        <h1>{otp_code}</h1>

        <p>
          Ce code est valable
          <strong>{settings.otp_expiry_minutes} minutes</strong>.
        </p>

        <p>
          Si vous n'êtes pas à l'origine de cette demande,
          vous pouvez simplement ignorer cet email.
        </p>

        <p>
          Cordialement,<br>
          L'équipe ArtikelBuddy
        </p>
      </body>
    </html>
    """

    data = {
        "sender": {
            "email": settings.smtp_from,
            "name": "ArtikelBuddy",
        },
        "to": [
            {
                "email": to_email,
            }
        ],
        "subject": "Votre code de sécurité – ArtikelBuddy",
        "textContent": text_body,
        "htmlContent": html_body,
    }

    response = requests.post(
        url,
        json=data,
        headers=headers,
        timeout=15,
    )

    response.raise_for_status()
