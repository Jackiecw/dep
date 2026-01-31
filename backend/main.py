from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise
from api import router as api_router

app = FastAPI(title="Internal Task System API")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routes
app.include_router(api_router)

# CORS Configuration
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:1420",  # Tauri dev
    "tauri://localhost",      # Tauri production (Windows)
    "https://tauri.localhost", # Tauri production (Newer)
    "*"                       # Allow all for now to be safe, or keep restricted if preferred
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    from models import User
    from auth import get_password_hash
    
    # Check if admin exists, if not create one
    admin = await User.get_or_none(username="admin")
    if not admin:
        await User.create(
            username="admin",
            password_hash=get_password_hash("admin123"),
            display_name="Administrator",
            role="admin"
        )
        print("Created default admin user: admin / admin123")

@app.get("/")
async def read_root():
    return {"message": "Internal Task System API v2.1 Running"}

import os

# Tortoise ORM Configuration
register_tortoise(
    app,
    db_url=os.getenv("DATABASE_URL", "sqlite://db.sqlite3"),
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
