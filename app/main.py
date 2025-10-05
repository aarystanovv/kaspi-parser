from fastapi import FastAPI
from .api.routes import router

app = FastAPI(title="Kaspi Parser API")
app.include_router(router)

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
