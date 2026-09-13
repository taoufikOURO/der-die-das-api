from fastapi import FastAPI

from app.routers import auth

app = FastAPI(title="Der Die Das API")

app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "API en ligne."}
