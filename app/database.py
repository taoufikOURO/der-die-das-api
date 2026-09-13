from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# Moteur de connexion à la base PostgreSQL (Supabase)
engine = create_engine(settings.database_url)

# Fabrique de sessions, une session par requête à l'API
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base dont hériteront tous les modèles SQLAlchemy
Base = declarative_base()


def get_db():
    """
    Dépendance FastAPI qui fournit une session de base de données
    et la referme automatiquement une fois la requête terminée.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
