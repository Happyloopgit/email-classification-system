"""FastAPI application setup."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from email_classification.api.router import router

# Create FastAPI app
app = FastAPI(
    title="Email Classification API",
    description="API for classifying emails and extracting information",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set appropriate origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router
app.include_router(router)

# Redirect root to docs
@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to documentation."""
    return RedirectResponse(url="/docs")

# Mount static files if they exist
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")