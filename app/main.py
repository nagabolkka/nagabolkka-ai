from fastapi import FastAPI

from app.config import settings

app = FastAPI(
    title="nagabolkka-ai",
    docs_url=None if settings.env == "prod" else "/docs",
)


@app.get("/ai/health")
def health():
    return {"status": "ok"}
