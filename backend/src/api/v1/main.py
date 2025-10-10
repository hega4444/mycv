import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.auth import router as auth_router
from src.api.v1.cvs import router as cvs_router
from src.api.v1.profile import router as profile_router
from src.api.v1.providers import router as providers_router
from src.api.v1.settings import router as settings_router

app = FastAPI(
    title="myCv Backend API",
    description="REST API for CV generation and management",
    version="1.0.0"
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(cvs_router)
app.include_router(settings_router)
app.include_router(providers_router)

@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "myCv Backend API"}

if __name__ == "__main__":
    uvicorn.run("src.api.v1.main:app", host="0.0.0.0", port=3000, reload=True)