from fastapi import FastAPI

from app.routers import auth, rush

app = FastAPI(title="Der Die Das API")

app.include_router(auth.router)
app.include_router(rush.router)


@app.get("/")
def root():
    return {"message": "API en ligne."}
