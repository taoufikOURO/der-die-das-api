from app.database import Base, engine
from app.models import (
    User,
    Word,
    Attempt,
)  # nécessaire pour que les tables soient détectées

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès.")
