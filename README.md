# SENTINEL - AI Vehicle Intelligence Grid

A multi-camera CCTV monitoring platform for vehicle tracking and ANPR.

## Architecture
- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **Backend**: FastAPI, Python, SQLAlchemy, SQLite (Development) / PostgreSQL (Production)
- **Computer Vision**: Abstracted pipelines for YOLO, ByteTrack, and OCR

## Getting Started

### Backend
1. `cd backend`
2. `python -m venv .venv`
3. Activate environment
4. `pip install -r requirements.txt` (or install manually as per instructions)
5. `python database/init_demo.py` (Initialize demo dataset)
6. `uvicorn main:app --reload`

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`

## Features Implemented
- Command Center Dashboard
- Dynamic Camera List
- Vehicle Search API
- Movement Timeline API
- Demo Data Initialization
