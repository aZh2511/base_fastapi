from fastapi import FastAPI
from presentation.api import auth


app = FastAPI(
    title="TODO",
    description="TODO",
    root_path="/api/v1",
)


@app.get("/healthcheck")
def healthcheck() -> dict:
    return {"status": "ok"}


app.include_router(auth.router)
