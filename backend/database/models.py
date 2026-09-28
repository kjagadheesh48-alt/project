from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Camera(Base):
    __tablename__ = "cameras"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String, unique=True, index=True)
    name = Column(String)
    location = Column(String)
    zone = Column(String)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    stream_type = Column(String)
    stream_url = Column(String)
    hls_url = Column(String, nullable=True)
    codec = Column(String)
    resolution = Column(String)
    status = Column(String, default="offline")
    last_seen = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, unique=True, index=True)
    vehicle_type = Column(String, nullable=True)
    color = Column(String, nullable=True)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class Detection(Base):
    __tablename__ = "detections"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String, ForeignKey("cameras.camera_id"), index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    plate_number = Column(String, index=True, nullable=True)
    object_class = Column(String)
    confidence = Column(Float)
    x1 = Column(Integer, nullable=True)
    y1 = Column(Integer, nullable=True)
    x2 = Column(Integer, nullable=True)
    y2 = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    pts_ms = Column(Integer, nullable=True)
    snapshot_url = Column(String, nullable=True)
    bounding_box = Column(JSON, nullable=True)
    tracking_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    camera = relationship("Camera")
    vehicle = relationship("Vehicle")

class CameraEvent(Base):
    __tablename__ = "camera_events"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String, ForeignKey("cameras.camera_id"), index=True)
    event_type = Column(String)
    message = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    severity = Column(String)
    
    camera = relationship("Camera")

class CameraZone(Base):
    __tablename__ = "camera_zones"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String, ForeignKey("cameras.camera_id"), index=True)
    zone_name = Column(String)
    polygon_coordinates = Column(JSON) # e.g. [{"x": 10, "y": 20}, ...]
    created_at = Column(DateTime, default=datetime.utcnow)
    
    camera = relationship("Camera")

class Watchlist(Base):
    __tablename__ = "watchlist"
    
    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, unique=True, index=True)
    priority = Column(String)
    reason = Column(String)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(Integer, ForeignKey("detections.id"), nullable=True)
    plate_number = Column(String, nullable=True)
    camera_id = Column(String, nullable=True)
    alert_type = Column(String)
    severity = Column(String)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged = Column(Boolean, default=False)
