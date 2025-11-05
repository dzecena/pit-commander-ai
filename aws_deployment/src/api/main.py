"""
GR Cup Analytics API - Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from typing import List, Optional
import json
import boto3
from datetime import datetime
import os
import csv
from io import StringIO

app = FastAPI(
    title="GR Cup Analytics API",
    description="Real-time telemetry analysis for GR Cup racing series",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Configuration
BUCKET_NAME = f"gr-cup-data-{os.getenv('STAGE', 'dev')}"
TABLE_NAME = f"gr-cup-telemetry-{os.getenv('STAGE', 'dev')}"

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "GR Cup Analytics API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "tracks": "/tracks",
            "telemetry": "/telemetry/{track_id}",
            "analytics": "/analytics/{track_id}",
            "dashboard": "/dashboard",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "gr-cup-analytics"
    }

@app.get("/tracks")
async def get_tracks():
    """Get list of available tracks"""
    tracks = {
        "BMP": {
            "name": "Barber Motorsports Park",
            "location": "Alabama, USA",
            "length": "2.38 miles",
            "turns": 17
        },
        "COTA": {
            "name": "Circuit of the Americas",
            "location": "Texas, USA", 
            "length": "3.426 miles",
            "turns": 20
        },
        "VIR": {
            "name": "Virginia International Raceway",
            "location": "Virginia, USA",
            "length": "3.27 miles", 
            "turns": 17
        },
        "SEB": {
            "name": "Sebring International Raceway",
            "location": "Florida, USA",
            "length": "3.74 miles",
            "turns": 17
        },
        "SON": {
            "name": "Sonoma Raceway",
            "location": "California, USA",
            "length": "2.52 miles",
            "turns": 12
        },
        "RA": {
            "name": "Road America",
            "location": "Wisconsin, USA",
            "length": "4.048 miles",
            "turns": 14
        },
        "INDY": {
            "name": "Indianapolis Motor Speedway",
            "location": "Indiana, USA",
            "length": "2.439 miles",
            "turns": 16
        }
    }
    
    return {
        "tracks": tracks,
        "total_tracks": len(tracks)
    }

@app.get("/telemetry/{track_id}")
async def get_telemetry(
    track_id: str,
    lap: Optional[int] = Query(None, description="Specific lap number"),
    limit: Optional[int] = Query(1000, description="Maximum number of records")
):
    """Get telemetry data for a specific track"""
    
    try:
        # Try to get data from S3
        key = f"processed-telemetry/{track_id}_telemetry_clean.csv"
        
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=key)
        df = pd.read_csv(response['Body'])
        
        # Filter by lap if specified
        if lap is not None:
            df = df[df['lap'] == lap]
        
        # Limit results
        df = df.head(limit)
        
        # Convert to JSON
        telemetry_data = df.to_dict('records')
        
        return {
            "track_id": track_id,
            "lap": lap,
            "data_points": len(telemetry_data),
            "telemetry": telemetry_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Telemetry data not found for track {track_id}")

@app.get("/analytics/{track_id}")
async def get_analytics(track_id: str):
    """Get analytics summary for a specific track"""
    
    try:
        # Get telemetry data
        key = f"processed-telemetry/{track_id}_telemetry_clean.csv"
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=key)
        df = pd.read_csv(response['Body'])
        
        # Calculate analytics
        analytics = {
            "track_id": track_id,
            "summary": {
                "total_laps": df['lap'].nunique(),
                "total_data_points": len(df),
                "max_speed": float(df['Speed'].max()),
                "avg_speed": float(df['Speed'].mean()),
                "min_speed": float(df['Speed'].min()),
                "max_braking": float(df['pbrake_f'].max()),
                "avg_throttle": float(df['ath'].mean()),
                "max_lateral_g": float(abs(df['accy_can']).max()),
                "max_steering_angle": float(abs(df['Steering_Angle']).max())
            },
            "lap_analysis": []
        }
        
        # Per-lap analysis
        for lap_num in sorted(df['lap'].unique()):
            lap_data = df[df['lap'] == lap_num]
            
            lap_stats = {
                "lap": int(lap_num),
                "max_speed": float(lap_data['Speed'].max()),
                "avg_speed": float(lap_data['Speed'].mean()),
                "min_speed": float(lap_data['Speed'].min()),
                "braking_events": int((lap_data['pbrake_f'] > 0).sum()),
                "avg_throttle": float(lap_data['ath'].mean()),
                "max_lateral_g": float(abs(lap_data['accy_can']).max()),
                "data_points": len(lap_data)
            }
            
            analytics["lap_analysis"].append(lap_stats)
        
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Analytics data not found for track {track_id}")

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the main dashboard HTML"""
    
    dashboard_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>GR Cup Analytics Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background-color: #f8f9fa; }
            .dashboard-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; }
            .track-card { transition: transform 0.2s; }
            .track-card:hover { transform: translateY(-5px); }
            .metric-card { background: white; border-radius: 10px; padding: 1.5rem; margin: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        </style>
    </head>
    <body>
        <div class="dashboard-header text-center">
            <h1>🏁 GR Cup Analytics Dashboard</h1>
            <p>Real-time telemetry analysis for all 7 GR Cup tracks</p>
        </div>
        
        <div class="container-fluid mt-4">
            <div class="row">
                <div class="col-md-3">
                    <div class="metric-card">
                        <h5>Track Selection</h5>
                        <select id="trackSelect" class="form-select">
                            <option value="">Select a track...</option>
                        </select>
                        <button id="loadTrack" class="btn btn-primary mt-2 w-100">Load Analytics</button>
                    </div>
                    
                    <div class="metric-card mt-3">
                        <h5>Quick Stats</h5>
                        <div id="quickStats">
                            <p>Select a track to view statistics</p>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-9">
                    <div class="metric-card">
                        <h5>Speed Analysis</h5>
                        <div id="speedChart" style="height: 400px;"></div>
                    </div>
                    
                    <div class="metric-card mt-3">
                        <h5>Lap Performance</h5>
                        <div id="lapChart" style="height: 400px;"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Load tracks on page load
            $(document).ready(function() {
                loadTracks();
            });
            
            function loadTracks() {
                $.get('/tracks', function(data) {
                    const select = $('#trackSelect');
                    Object.keys(data.tracks).forEach(function(trackId) {
                        const track = data.tracks[trackId];
                        select.append(`<option value="${trackId}">${track.name}</option>`);
                    });
                });
            }
            
            $('#loadTrack').click(function() {
                const trackId = $('#trackSelect').val();
                if (trackId) {
                    loadTrackAnalytics(trackId);
                }
            });
            
            function loadTrackAnalytics(trackId) {
                $.get(`/analytics/${trackId}`, function(data) {
                    updateQuickStats(data);
                    createSpeedChart(data);
                    createLapChart(data);
                });
            }
            
            function updateQuickStats(data) {
                const stats = data.summary;
                const html = `
                    <p><strong>Total Laps:</strong> ${stats.total_laps}</p>
                    <p><strong>Max Speed:</strong> ${stats.max_speed.toFixed(1)} mph</p>
                    <p><strong>Avg Speed:</strong> ${stats.avg_speed.toFixed(1)} mph</p>
                    <p><strong>Max Braking:</strong> ${stats.max_braking.toFixed(1)}</p>
                    <p><strong>Max Lateral G:</strong> ${stats.max_lateral_g.toFixed(2)}g</p>
                `;
                $('#quickStats').html(html);
            }
            
            function createSpeedChart(data) {
                const laps = data.lap_analysis.map(lap => lap.lap);
                const maxSpeeds = data.lap_analysis.map(lap => lap.max_speed);
                const avgSpeeds = data.lap_analysis.map(lap => lap.avg_speed);
                
                const trace1 = {
                    x: laps,
                    y: maxSpeeds,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Max Speed',
                    line: { color: 'blue' }
                };
                
                const trace2 = {
                    x: laps,
                    y: avgSpeeds,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Avg Speed',
                    line: { color: 'green' }
                };
                
                const layout = {
                    title: 'Speed by Lap',
                    xaxis: { title: 'Lap Number' },
                    yaxis: { title: 'Speed (mph)' }
                };
                
                Plotly.newPlot('speedChart', [trace1, trace2], layout);
            }
            
            function createLapChart(data) {
                const laps = data.lap_analysis.map(lap => lap.lap);
                const brakingEvents = data.lap_analysis.map(lap => lap.braking_events);
                
                const trace = {
                    x: laps,
                    y: brakingEvents,
                    type: 'bar',
                    name: 'Braking Events',
                    marker: { color: 'red' }
                };
                
                const layout = {
                    title: 'Braking Events by Lap',
                    xaxis: { title: 'Lap Number' },
                    yaxis: { title: 'Number of Braking Events' }
                };
                
                Plotly.newPlot('lapChart', [trace], layout);
            }
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=dashboard_html)