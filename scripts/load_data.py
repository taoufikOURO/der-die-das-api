import pandas as pd

from app.database import SessionLocal
from app.models import Word

CSV_PATH = "data/nouns.csv"


def load_words():
    """
    Charge les mots depuis le fichier CSV et les insère dans la base de données.
    """

    df = pd.read_csv(CSV_PATH)

    db = SessionLocal()
    try:
        count_inserted = 0
        count_skipped = 0

        for _, row in df.iterrows():
            # Vérifie que le mot n'existe pas déjà en base (évite les doublons si le script est relancé)
            existing = db.query(Word).filter(Word.word == row["mot"]).first()
            if existing:
                count_skipped += 1
                continue

            word = Word(
                word=row["mot"],
                article=row["article"],
                level=row["niveau"] if pd.notna(row["niveau"]) else None,
                fr_translation=(
                    row["traduction_fr"] if pd.notna(row["traduction_fr"]) else None
                ),
                en_translation=(
                    row["traduction_en"] if pd.notna(row["traduction_en"]) else None
                ),
            )
            db.add(word)
            count_inserted += 1

        db.commit()
        print(
            f"{count_inserted} mots insérés, {count_skipped} déjà présents (ignorés)."
        )
    finally:
        db.close()


if __name__ == "__main__":
    load_words()
