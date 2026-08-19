from contextlib import asynccontextmanager
from fastapi import FastAPI
from database.connection import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs when the application starts 
    init_db()
    yield
    # Runs when the application shuts down 

app = FastAPI(title="E-commerce API", lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "E-commerce API running"}