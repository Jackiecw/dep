from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Internal Task System API")

# Mount static files for version checking and updates
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return {"message": "Internal Task System API v2.1"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
