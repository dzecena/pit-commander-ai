"""
FastAPI server for real-time telemetry and predictions

Author: GR Cup Analytics Team
Date: 2025-10-30

Endpoints:
- GET /: Health check
- GET /tracks: List available tracks
- GET /track/{track_id}/summary: Track characteristics
- POST /predict/lap-time: Predict lap time
- POST /strategy/pit-window: Calculate pit window
- WebSocket /ws/telemetry/{track_id}: Live telemetry stream
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
import json
import logging
import pandas as pd
from pathlib import Path
import sys

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from models.tire_degradation import TireDegradationModel
from models.pit_strategy import PitStrategyOptimizer
from utils.config import TRACKS, API_CONFIG

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="GR Cup Analytics API",
    description="Real-time race strategy and telemetry analysis",
    version="1.0.0"
)

# Enable CORS for React dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=API_CONFIG['cors_origins'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instances
tire_model = TireDegradationModel()
pit_optimizer = None

# Load models on startup
@app.on_event("startup")
async def startup_event():
    global pit_optimizer
    logger.info("Starting GR Cup Analytics API...")
    
    # Try to load pre-trained model
    if tire_model.load_model():
        logger.info("Loaded pre-trained tire degradation model")
        pit_optimizer = PitStrategyOptimizer(tire_model)
    else:
        logger.warning("No pre-trained model found - predictions will be limited")

# Pydantic models for request validation
class LapTimePredictionRequest(BaseModel):
    tire_age: int
    track_id: str
    driver_avg_pace: float
    current_pace: float
    track_avg_speed: Optional[float] = 150.0
    race_progress: Optional[float] = 0.5

class PitWindowRequest(BaseModel):
    current_lap: int
    track_id: str
    position: int
    gap_ahead: float
    gap_behind: float
    tire_age: Optional[int] = None
    max_laps: Optional[int] = 30

# Health check endpoint
@app.get("/")
async def root():
    return {
        "status": "GR Cup Analytics API",
        "version": "1.0.0",
        "model_loaded": tire_model.is_trained,
        "tracks_available": len(TRACKS)
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_status": "loaded" if tire_model.is_trained else "not_loaded",
        "timestamp": pd.Timestamp.now().isoformat()
    }

@app.get("/tracks")
async def get_tracks():
    """
    Return list of available tracks with metadata
    """
    tracks_info = []
    
    for track_id, track_config in TRACKS.items():
        # Check if track data exists
        data_path = Path(f"data/cleaned/{track_id}_telemetry_clean.csv")
        data_available = data_path.exists()
        
        tracks_info.append({
            "id": track_id,
            "name": track_config["name"],
            "folder": track_config["folder"],
            "typical_lap_time": track_config["typical_lap_time"],
            "sectors": track_config["sectors"],
            "data_available": data_available
        })
    
    return {
        "tracks": tracks_info,
        "total_tracks": len(tracks_info)
    }

@app.get("/track/{track_id}/summary")
async def get_track_summary(track_id: str):
    """
    Return track characteristics, lap records, sector info
    """
    if track_id not in TRACKS:
        raise HTTPException(status_code=404, detail="Track not found")
    
    track_config = TRACKS[track_id]
    
    # Try to load track data for more detailed summary
    summary = {
        "id": track_id,
        "name": track_config["name"],
        "typical_lap_time": track_config["typical_lap_time"],
        "sectors": track_config["sectors"],
        "characteristics": {}
    }
    
    try:
        # Load cleaned data if available
        data_path = Path(f"data/cleaned/{track_id}_telemetry_clean.csv")
        if data_path.exists():
            df = pd.read_csv(data_path)
            
            if not df.empty:
                summary["characteristics"] = {
                    "total_records": len(df),
                    "avg_speed": float(df["Speed"].mean()) if "Speed" in df.columns else None,
                    "max_speed": float(df["Speed"].max()) if "Speed" in df.columns else None,
                    "unique_cars": int(df["car_number"].nunique()) if "car_number" in df.columns else None,
                    "total_laps": int(df["lap"].max()) if "lap" in df.columns else None
                }
    
    except Exception as e:
        logger.error(f"Error loading track summary for {track_id}: {e}")
    
    return summary

@app.post("/predict/lap-time")
async def predict_lap_time(request: LapTimePredictionRequest):
    """
    Input: {
        'tire_age': int,
        'track_id': str,
        'driver_avg_pace': float,
        'current_pace': float
    }
    Output: {
        'predicted_time': float,
        'confidence': float,
        'recommendation': str
    }
    """
    if not tire_model.is_trained:
        raise HTTPException(status_code=503, detail="Model not available")
    
    if request.track_id not in TRACKS:
        raise HTTPException(status_code=400, detail="Invalid track ID")
    
    try:
        # Prepare features
        track_config = TRACKS[request.track_id]
        
        features = {
            'tire_age': request.tire_age,
            'driver_avg_pace': request.driver_avg_pace,
            'track_avg_speed': request.track_avg_speed,
            'track_degradation_rate': 0.5,  # Default, could be loaded from data
            'race_progress': request.race_progress,
            'recent_pace_3lap': request.current_pace,
            'session_best': track_config['typical_lap_time'] * 0.95,  # Estimate
            'track_type_encoded': 1 if request.track_avg_speed > 150 else 0
        }
        
        # Make prediction
        prediction = tire_model.predict_lap_time(features)
        
        # Generate recommendation
        if prediction['predicted_time'] > request.driver_avg_pace + 1.0:
            recommendation = "Consider pitting - significant tire degradation detected"
        elif prediction['predicted_time'] > request.driver_avg_pace + 0.5:
            recommendation = "Monitor tire performance - degradation increasing"
        else:
            recommendation = "Tires performing well - continue current stint"
        
        return {
            "predicted_time": prediction['predicted_time'],
            "confidence": prediction['confidence'],
            "uncertainty": prediction['uncertainty'],
            "recommendation": recommendation,
            "track_id": request.track_id,
            "features_used": features
        }
        
    except Exception as e:
        logger.error(f"Error predicting lap time: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")

@app.post("/strategy/pit-window")
async def calculate_pit_window(request: PitWindowRequest):
    """
    Input: {
        'current_lap': int,
        'track_id': str,
        'position': int,
        'gap_ahead': float,
        'gap_behind': float
    }
    Output: Pit recommendation with scenarios
    """
    if not pit_optimizer:
        raise HTTPException(status_code=503, detail="Pit strategy optimizer not available")
    
    if request.track_id not in TRACKS:
        raise HTTPException(status_code=400, detail="Invalid track ID")
    
    try:
        track_config = TRACKS[request.track_id]
        
        # Prepare current state
        current_state = {
            'current_lap': request.current_lap,
            'max_laps': request.max_laps,
            'position': request.position,
            'gap_ahead': request.gap_ahead,
            'gap_behind': request.gap_behind,
            'track_features': {
                'tire_age': request.tire_age or request.current_lap,
                'driver_avg_pace': track_config['typical_lap_time'],
                'track_avg_speed': 150.0,  # Default
                'track_degradation_rate': 0.5,  # Default
                'race_progress': request.current_lap / request.max_laps,
                'recent_pace_3lap': track_config['typical_lap_time'],
                'session_best': track_config['typical_lap_time'] * 0.95,
                'track_type_encoded': 1
            }
        }
        
        # Get recommendation
        recommendation = pit_optimizer.get_recommendation(current_state)
        
        return {
            "track_id": request.track_id,
            "current_lap": request.current_lap,
            "recommendation": recommendation,
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error calculating pit window: {e}")
        raise HTTPException(status_code=500, detail="Pit strategy calculation failed")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.websocket("/ws/telemetry/{track_id}")
async def telemetry_stream(websocket: WebSocket, track_id: str):
    """
    WebSocket for streaming live telemetry during race replay
    Sends updates every 100ms
    """
    if track_id not in TRACKS:
        await websocket.close(code=4000, reason="Invalid track ID")
        return
    
    await manager.connect(websocket)
    logger.info(f"WebSocket connected for track {track_id}")
    
    try:
        # Load race data for replay
        data_path = Path(f"data/cleaned/{track_id}_telemetry_clean.csv")
        
        if not data_path.exists():
            await websocket.send_text(json.dumps({
                "error": "No data available for this track",
                "track_id": track_id
            }))
            return
        
        # Load and prepare data
        df = pd.read_csv(data_path)
        
        if df.empty:
            await websocket.send_text(json.dumps({
                "error": "Empty dataset",
                "track_id": track_id
            }))
            return
        
        # Sort by timestamp for replay
        df = df.sort_values('timestamp')
        
        # Stream data lap by lap
        current_lap = 1
        max_lap = df['lap'].max() if 'lap' in df.columns else 30
        
        while current_lap <= max_lap:
            try:
                # Get current lap data
                lap_data = df[df['lap'] == current_lap] if 'lap' in df.columns else df.head(100)
                
                if not lap_data.empty:
                    # Prepare telemetry update
                    update = {
                        "track_id": track_id,
                        "current_lap": current_lap,
                        "max_lap": int(max_lap),
                        "timestamp": pd.Timestamp.now().isoformat(),
                        "telemetry": {
                            "speed": float(lap_data['Speed'].mean()) if 'Speed' in lap_data.columns else 0,
                            "brake_pressure": float(lap_data['pbrake_f'].mean()) if 'pbrake_f' in lap_data.columns else 0,
                            "throttle": float(lap_data['ath'].mean()) if 'ath' in lap_data.columns else 0,
                            "steering_angle": float(lap_data['Steering_Angle'].mean()) if 'Steering_Angle' in lap_data.columns else 0
                        }
                    }
                    
                    # Add predictions if model is available
                    if tire_model.is_trained:
                        features = {
                            'tire_age': current_lap,
                            'driver_avg_pace': TRACKS[track_id]['typical_lap_time'],
                            'track_avg_speed': update['telemetry']['speed'],
                            'track_degradation_rate': 0.5,
                            'race_progress': current_lap / max_lap,
                            'recent_pace_3lap': TRACKS[track_id]['typical_lap_time'],
                            'session_best': TRACKS[track_id]['typical_lap_time'] * 0.95,
                            'track_type_encoded': 1
                        }
                        
                        prediction = tire_model.predict_lap_time(features)
                        update['predictions'] = prediction
                        
                        # Add pit strategy if available
                        if pit_optimizer:
                            pit_state = {
                                'current_lap': current_lap,
                                'max_laps': int(max_lap),
                                'position': 3,  # Default position
                                'gap_ahead': 2.0,
                                'gap_behind': 3.0,
                                'track_features': features
                            }
                            
                            pit_recommendation = pit_optimizer.get_recommendation(pit_state)
                            update['pit_strategy'] = pit_recommendation
                    
                    # Send update
                    await websocket.send_text(json.dumps(update))
                
                current_lap += 1
                
                # Wait 100ms for real-time feel (10x speed)
                await asyncio.sleep(0.1)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in telemetry stream: {e}")
                break
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for track {track_id}")
    except Exception as e:
        logger.error(f"WebSocket error for track {track_id}: {e}")
    finally:
        manager.disconnect(websocket)

# Additional utility endpoints
@app.get("/model/status")
async def model_status():
    """Get current model status and metrics"""
    if not tire_model.is_trained:
        return {"status": "not_loaded", "metrics": {}}
    
    return {
        "status": "loaded",
        "metrics": tire_model.training_metrics,
        "features": tire_model.feature_names
    }

@app.get("/model/feature-importance")
async def get_feature_importance():
    """Get model feature importance"""
    if not tire_model.is_trained:
        raise HTTPException(status_code=503, detail="Model not available")
    
    importance_df = tire_model.get_feature_importance()
    
    if importance_df.empty:
        return {"features": []}
    
    return {
        "features": importance_df.to_dict('records')
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=API_CONFIG['host'],
        port=API_CONFIG['port'],
        reload=True,
        log_level="info"
    )