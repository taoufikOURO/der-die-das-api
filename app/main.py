from fastapi import FastAPI

from app.routers import auth, rush, users, words
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(title="Der Die Das API")

# Ajouter le middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(rush.router)
app.include_router(users.router)
app.include_router(words.router)


@app.get("/")
def root():
    return {"message": "API en ligne."}
