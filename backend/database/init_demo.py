import os
import sys
from datetime import datetime, timedelta
import random

# Add parent dir to path so we can import from database
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.connection import SessionLocal, engine
from database.models import Base, Camera, Vehicle, Detection, Watchlist, Alert

def init_demo_data():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Create Demo Cameras
    cameras = [
        Camera(camera_id="CAM-01", name="Main Gate", location="Ahmedabad Central", zone="North", latitude=23.0225, longitude=72.5714, stream_type="RTSP", stream_url="rtsp://demo/01", codec="H264", resolution="1920x1080", status="online"),
        Camera(camera_id="CAM-02", name="Ring Road North", location="Ahmedabad North", zone="North", latitude=23.0525, longitude=72.5814, stream_type="RTSP", stream_url="rtsp://demo/02", codec="H264", resolution="1920x1080", status="online"),
        Camera(camera_id="CAM-03", name="Railway Junction", location="Ahmedabad East", zone="East", latitude=23.0225, longitude=72.6014, stream_type="RTSP", stream_url="rtsp://demo/03", codec="H264", resolution="1920x1080", status="online"),
        Camera(camera_id="CAM-04", name="City Center", location="Ahmedabad Center", zone="Center", latitude=23.0325, longitude=72.5814, stream_type="RTSP", stream_url="rtsp://demo/04", codec="H264", resolution="1920x1080", status="reconnecting"),
        Camera(camera_id="CAM-05", name="Industrial Estate", location="Ahmedabad South", zone="South", latitude=22.9925, longitude=72.5814, stream_type="RTSP", stream_url="rtsp://demo/05", codec="H264", resolution="1920x1080", status="online"),
        Camera(camera_id="CAM-06", name="Airport Road", location="Ahmedabad Northeast", zone="Northeast", latitude=23.0725, longitude=72.6214, stream_type="RTSP", stream_url="rtsp://demo/06", codec="H264", resolution="1920x1080", status="offline"),
    ]
    db.add_all(cameras)
    db.commit()
    
    # Create Demo Vehicles
    plates = ["GJ01AB1234", "GJ01XY7788", "GJ05MN2026", "TN38CQ7788", "KA05MN2026", "MH12AB4521"]
    v_types = ["Car", "SUV", "Truck", "Car", "Truck", "Motorcycle"]
    
    now = datetime.utcnow()
    
    for i, plate in enumerate(plates):
        v = Vehicle(plate_number=plate, vehicle_type=v_types[i], color="White")
        db.add(v)
    db.commit()
    
    # Create Demo Detections (History)
    # Target scenario: GJ01AB1234 movement CAM-01 -> CAM-03 -> CAM-05 -> CAM-02 today
    
    base_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    scenario = [
        {"cam": "CAM-01", "time": "09:12:44"},
        {"cam": "CAM-03", "time": "09:28:19"},
        {"cam": "CAM-05", "time": "10:04:07"},
        {"cam": "CAM-02", "time": "18:41:03"},
    ]
    
    vehicle_obj = db.query(Vehicle).filter_by(plate_number="GJ01AB1234").first()
    
    for evt in scenario:
        dt = datetime.strptime(f"{base_date.strftime('%Y-%m-%d')} {evt['time']}", "%Y-%m-%d %H:%M:%S")
        d = Detection(
            camera_id=evt['cam'],
            vehicle_id=vehicle_obj.id,
            plate_number="GJ01AB1234",
            vehicle_type="Car",
            detected_at=dt,
            confidence=round(random.uniform(0.88, 0.99), 3),
        )
        db.add(d)
        
    # Generate random detections for other vehicles across the last 7 days
    cam_ids = [c.camera_id for c in cameras]
    for _ in range(100):
        plate = random.choice(plates)
        v = db.query(Vehicle).filter_by(plate_number=plate).first()
        days_ago = random.randint(0, 7)
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        dt = base_date - timedelta(days=days_ago) + timedelta(hours=hour, minutes=minute)
        
        d = Detection(
            camera_id=random.choice(cam_ids),
            vehicle_id=v.id,
            plate_number=plate,
            vehicle_type=v.vehicle_type,
            detected_at=dt,
            confidence=round(random.uniform(0.70, 0.99), 3)
        )
        db.add(d)
        
    db.commit()
    
    # Add a watchlist entry
    wl = Watchlist(plate_number="MH12AB4521", priority="HIGH", reason="Investigation", active=True)
    db.add(wl)
    db.commit()
    
    print("Demo data initialized successfully.")

if __name__ == "__main__":
    init_demo_data()
