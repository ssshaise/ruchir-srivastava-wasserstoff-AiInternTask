from fastapi import FastAPI

from .api.endpoints import router as api_router

app = FastAPI(title="ReasearchGPT")

app.include_router(api_router)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the API!"}