import time
import random
import sys
import os
from datetime import datetime

# Add parent dir to path so we can import from database
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.connection import SessionLocal
from database.models import Detection, Vehicle, Camera

def run_ml_simulator():
    print("Starting ML Tracking Simulator...")
    db = SessionLocal()
    
    cameras = db.query(Camera).all()
    cam_ids = [c.camera_id for c in cameras]
    
    if not cam_ids:
        print("No cameras found. Run init_demo.py first.")
        return
        
    plates = ["MH14DX5566", "GJ01XY7788", "GJ05MN2026", "TN38CQ7788", "KA05MN2026", "MH12AB4521", "RJ14CX9090", "DL8CAF9000"]
    v_types = ["Car", "SUV", "Truck", "Motorcycle", "Bus"]
    
    print(f"Tracking ML engine initialized on {len(cam_ids)} camera streams.")
    
    while True:
        try:
            # Simulate a detection event every 3 to 8 seconds
            time.sleep(random.randint(3, 8))
            
            cam_id = random.choice(cam_ids)
            plate = random.choice(plates)
            v_type = random.choice(v_types)
            
            # Check if vehicle exists in DB, if not, it will just use a generic ID for simulation
            vehicle = db.query(Vehicle).filter_by(plate_number=plate).first()
            vehicle_id = vehicle.id if vehicle else 1
            
            # Create a new detection
            d = Detection(
                camera_id=cam_id,
                vehicle_id=vehicle_id,
                plate_number=plate,
                vehicle_type=v_type,
                detected_at=datetime.utcnow(),
                confidence=round(random.uniform(0.75, 0.99), 3)
            )
            
            db.add(d)
            db.commit()
            
            print(f"[ML ENGINE] Detected {plate} ({v_type}) on {cam_id} with {d.confidence*100:.1f}% confidence. Speed: ~{random.randint(40, 80)} km/h")
            
        except Exception as e:
            print(f"Error in ML pipeline: {e}")
            db.rollback()

if __name__ == "__main__":
    run_ml_simulator()
