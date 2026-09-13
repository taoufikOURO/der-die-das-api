import uuid
from datetime import datetime, timezone


def generate_id() -> str:
    """
    Génère un identifiant unique de 32 caractères (UUID4 sans tirets),
    utilisé comme clé primaire pour les entités exposées via l'API.
    """
    return uuid.uuid4().hex


def utc_now() -> datetime:
    """Retourne l'horodatage UTC courant, utilisé comme valeur par défaut."""
    return datetime.now(timezone.utc)