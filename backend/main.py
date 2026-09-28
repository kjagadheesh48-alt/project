from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database.connection import engine, get_db
from database import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SENTINEL API", version="1.0.0")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "Sentinel Backend"}

@app.get("/api/cameras")
def get_cameras(db: Session = Depends(get_db)):
    cameras = db.query(models.Camera).all()
    return cameras

@app.get("/api/cameras/{camera_id}/detections")
def get_camera_detections(camera_id: str, date: str = None, db: Session = Depends(get_db)):
    query = db.query(models.Detection).filter(models.Detection.camera_id == camera_id)
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
            next_date = target_date + timedelta(days=1)
            query = query.filter(models.Detection.detected_at >= target_date, models.Detection.detected_at < next_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
            
    query = query.order_by(models.Detection.detected_at.asc())
    return query.all()

@app.get("/api/vehicles/search")
def search_vehicles(q: str, db: Session = Depends(get_db)):
    if not q:
        return []
    q_normalized = q.replace(" ", "").replace("-", "").upper()
    vehicles = db.query(models.Vehicle).filter(models.Vehicle.plate_number.like(f"%{q_normalized}%")).limit(50).all()
    return vehicles

@app.get("/api/vehicles/{plate_number}/history")
def get_vehicle_history(plate_number: str, db: Session = Depends(get_db)):
    plate_normalized = plate_number.replace(" ", "").replace("-", "").upper()
    detections = db.query(models.Detection).filter(
        models.Detection.plate_number == plate_normalized
    ).order_by(models.Detection.detected_at.asc()).all()
    
    return detections

@app.get("/api/watchlist")
def get_watchlist(db: Session = Depends(get_db)):
    return db.query(models.Watchlist).all()

@app.get("/api/alerts")
def get_alerts(db: Session = Depends(get_db)):
    return db.query(models.Alert).order_by(models.Alert.created_at.desc()).limit(100).all()

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    total_cameras = db.query(models.Camera).count()
    active_cameras = db.query(models.Camera).filter(models.Camera.status == "online").count()
    
    today = datetime.utcnow().date()
    vehicles_today = db.query(models.Detection).filter(models.Detection.detected_at >= today).count()
    watchlist_matches = db.query(models.Alert).filter(models.Alert.alert_type == "watchlist_match").count()
    
    return {
        "total_cameras": total_cameras,
        "active_cameras": active_cameras,
        "vehicles_today": vehicles_today,
        "watchlist_matches": watchlist_matches
    }

from fastapi import WebSocket, WebSocketDisconnect
from websocket.manager import manager
import asyncio

@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We'll just wait for messages from the client if needed
            # In a real app, AI inference would push messages to `manager.broadcast`
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
