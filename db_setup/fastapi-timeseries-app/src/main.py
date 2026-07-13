from fastapi import FastAPI
from src.database.connection import create_db_connection
from src.api.routes import router as time_series_router

app = FastAPI()

# Initialize database connection
create_db_connection()

# Include API routes
app.include_router(time_series_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Time Series Application!"}