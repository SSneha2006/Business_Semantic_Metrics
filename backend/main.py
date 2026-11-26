from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import Base, engine
from backend.models.user import User, Workspace
from backend.models.dataset import Dataset
from backend.routers.auth import router as auth_router
from backend.routers.datasets import router as datasets_router
from backend.models.metric import Metric
from backend.routers.metrics import router as metrics_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Business Semantic Metrics API",
    version="1.0.0"
)

# Enable frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(auth_router, prefix="/api")
app.include_router(datasets_router, prefix="/api")
app.include_router(metrics_router, prefix="/api")


@app.get("/")
def home():
    return {
        "message": "Business Semantic Metrics Backend is running"
    }



from backend.models.metric import Metric
from backend.routers.metrics import router as metrics_router@app.get("/health")
def health():
    return {
        "status": "healthy",
        "backend": "local"
    }