from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise
from api import router as api_router

app = FastAPI(title="Internal Task System API")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routes
app.include_router(api_router)

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

# Tortoise ORM Configuration
register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",  # For local MVP development, use SQLite. In Prod use Postgres.
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
