from fastapi import FastAPI

from app.routers import auth, rush, users, words

app = FastAPI(title="Der Die Das API")

app.include_router(auth.router)
app.include_router(rush.router)
app.include_router(users.router)
app.include_router(words.router)


@app.get("/")
def root():
    return {"message": "API en ligne."}
