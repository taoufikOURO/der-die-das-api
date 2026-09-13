from pydantic import BaseModel


class WordQuestion(BaseModel):
    """Mot envoyé au joueur pendant un rush : jamais l'article, c'est ce qu'on lui demande de trouver."""

    id: str
    word: str
    fr_translation: str | None
    en_translation: str | None

    class Config:
        from_attributes = True


class WordOut(BaseModel):
    """Mot complet, utilisé après coup (résultat, révision, dashboard) : l'article est révélé."""

    id: str
    word: str
    article: str
    level: str | None
    fr_translation: str | None
    en_translation: str | None

    class Config:
        from_attributes = True
