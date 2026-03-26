from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .database import engine, Base
from .routes import projects, admin

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Project Registry & Duplicate Detection System",
    description="API for academic project registry using NLP for duplicate detection",
    version="1.0.0"
)

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"message": "Welcome to Project Registry & Duplicate Detection System API"}
