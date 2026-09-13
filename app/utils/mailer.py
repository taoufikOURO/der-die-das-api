import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import settings


def send_otp_email(to_email: str, otp_code: str) -> None:
    """
    Envoie le code OTP à l'adresse email fournie, pour validation
    de l'adresse à l'inscription (ou renvoi en cas de nouvelle demande).
    """

    message = MIMEMultipart("alternative")
    message["Subject"] = "Validation de votre adresse email"
    message["From"] = settings.smtp_from
    message["To"] = to_email

    text_body = (
        f"Voici votre code de validation : {otp_code}\n\n"
        f"Ce code est valable {settings.otp_expiry_minutes} minutes."
    )

    html_body = f"""
    <html>
      <body>
        <p>Voici votre code de validation :</p>
        <h2>{otp_code}</h2>
        <p>Ce code est valable {settings.otp_expiry_minutes} minutes.</p>
      </body>
    </html>
    """

    message.attach(MIMEText(text_body, "plain"))
    message.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_username, settings.smtp_password)
        server.sendmail(settings.smtp_from, to_email, message.as_string())
