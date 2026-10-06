import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.models.database import init_db
from backend.app.api.incidents import router as api_router
from backend.app.api.websockets import ws_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("incidentzero")

# Ensure tables exist
init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing IncidentZero database tables...")
    init_db()
    logger.info(f"IncidentZero backend operational. Model configured: {settings.NEBIUS_MODEL}")
    yield
    logger.info("IncidentZero backend shutting down.")

app = FastAPI(
    title="INCIDENTZERO - Autonomous AI Incident Commander",
    description="Production-grade AI operations and incident commander powered by NVIDIA Nemotron on Nebius Token Factory",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for hackathon / local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include REST API routes
app.include_router(api_router)

@app.get("/")
def root():
    return {
        "service": "INCIDENTZERO API",
        "status": "ONLINE",
        "hackathon": "NVIDIA x Nebius Global AI Hackathon",
        "model": settings.NEBIUS_MODEL,
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "HEALTHY"}

# Live WebSocket streams
@app.websocket("/ws")
async def websocket_global_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket, incident_id="global")
    try:
        while True:
            # Keepalive receiver
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, incident_id="global")

@app.websocket("/ws/investigation/{incident_id}")
async def websocket_incident_endpoint(websocket: WebSocket, incident_id: str):
    await ws_manager.connect(websocket, incident_id=incident_id)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, incident_id=incident_id)
