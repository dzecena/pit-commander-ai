"""
GR Cup Analytics API - Simplified Version (No Pandas)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from typing import List, Optional
import json
import boto3
from datetime import datetime
import os

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

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "GR Cup Analytics API",
        "version": "1.0.0",
        "status": "active",
        "message": "🏁 Welcome to GR Cup Analytics!",
        "endpoints": {
            "tracks": "/tracks",
            "demo": "/demo",
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
        "service": "gr-cup-analytics",
        "message": "🏎️ All systems operational!"
    }

@app.get("/tracks")
async def get_tracks():
    """Get list of available tracks"""
    tracks = {
        "BMP": {
            "name": "Barber Motorsports Park",
            "location": "Alabama, USA",
            "length": "2.38 miles",
            "turns": 17,
            "status": "active"
        },
        "COTA": {
            "name": "Circuit of the Americas",
            "location": "Texas, USA", 
            "length": "3.426 miles",
            "turns": 20,
            "status": "active"
        },
        "VIR": {
            "name": "Virginia International Raceway",
            "location": "Virginia, USA",
            "length": "3.27 miles", 
            "turns": 17,
            "status": "active"
        },
        "SEB": {
            "name": "Sebring International Raceway",
            "location": "Florida, USA",
            "length": "3.74 miles",
            "turns": 17,
            "status": "active"
        },
        "SON": {
            "name": "Sonoma Raceway",
            "location": "California, USA",
            "length": "2.52 miles",
            "turns": 12,
            "status": "active"
        },
        "RA": {
            "name": "Road America",
            "location": "Wisconsin, USA",
            "length": "4.048 miles",
            "turns": 14,
            "status": "active"
        },
        "INDY": {
            "name": "Indianapolis Motor Speedway",
            "location": "Indiana, USA",
            "length": "2.439 miles",
            "turns": 16,
            "status": "active"
        }
    }
    
    return {
        "tracks": tracks,
        "total_tracks": len(tracks),
        "message": "🏁 All GR Cup tracks available for analysis"
    }

@app.get("/demo")
async def get_demo_data():
    """Get demo telemetry data"""
    demo_data = {
        "track_id": "BMP",
        "track_name": "Barber Motorsports Park",
        "demo_telemetry": [
            {
                "lap": 1,
                "speed": 145.2,
                "throttle": 85.5,
                "brake": 0.0,
                "steering": -2.1,
                "lateral_g": 0.8,
                "sector": "S1"
            },
            {
                "lap": 1,
                "speed": 132.8,
                "throttle": 65.2,
                "brake": 45.0,
                "steering": 15.3,
                "lateral_g": 1.2,
                "sector": "S1"
            },
            {
                "lap": 1,
                "speed": 98.5,
                "throttle": 25.0,
                "brake": 85.0,
                "steering": 25.8,
                "lateral_g": 1.8,
                "sector": "S2"
            }
        ],
        "analytics": {
            "max_speed": 145.2,
            "avg_speed": 125.5,
            "max_braking": 85.0,
            "max_lateral_g": 1.8,
            "total_data_points": 3
        }
    }
    
    return demo_data

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the main dashboard HTML"""
    
    dashboard_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🏁 GR Cup Analytics Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                min-height: 100vh;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .dashboard-container { 
                background: rgba(255,255,255,0.95); 
                border-radius: 15px; 
                margin: 20px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .track-card { 
                background: white;
                border-radius: 10px;
                padding: 20px;
                margin: 10px 0;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            }
            .track-card:hover { 
                transform: translateY(-5px);
                box-shadow: 0 8px 15px rgba(0,0,0,0.2);
            }
            .metric-badge {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                padding: 10px 20px;
                border-radius: 25px;
                display: inline-block;
                margin: 5px;
                font-weight: bold;
            }
            .status-active {
                color: #28a745;
                font-weight: bold;
            }
            .header-title {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
        </style>
    </head>
    <body>
        <div class="container-fluid">
            <div class="dashboard-container">
                <h1 class="header-title">🏁 GR Cup Analytics Dashboard</h1>
                <p class="text-center lead">Real-time telemetry analysis for all 7 GR Cup tracks</p>
                
                <div class="row">
                    <div class="col-md-6">
                        <div class="track-card">
                            <h3>📊 System Status</h3>
                            <div class="metric-badge">API: Online</div>
                            <div class="metric-badge">Tracks: 7 Active</div>
                            <div class="metric-badge">Data: Ready</div>
                        </div>
                        
                        <div class="track-card">
                            <h3>🎯 Quick Demo</h3>
                            <button class="btn btn-primary" onclick="loadDemo()">Load Demo Data</button>
                            <div id="demoResults" class="mt-3"></div>
                        </div>
                    </div>
                    
                    <div class="col-md-6">
                        <div class="track-card">
                            <h3>🏎️ Available Tracks</h3>
                            <div id="tracksList">Loading tracks...</div>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-12">
                        <div class="track-card">
                            <h3>🚀 API Endpoints</h3>
                            <div class="row">
                                <div class="col-md-3">
                                    <strong>GET /tracks</strong><br>
                                    <small>List all tracks</small>
                                </div>
                                <div class="col-md-3">
                                    <strong>GET /demo</strong><br>
                                    <small>Demo telemetry data</small>
                                </div>
                                <div class="col-md-3">
                                    <strong>GET /health</strong><br>
                                    <small>System health check</small>
                                </div>
                                <div class="col-md-3">
                                    <strong>GET /dashboard</strong><br>
                                    <small>This dashboard</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Load tracks on page load
            fetch('/tracks')
                .then(response => response.json())
                .then(data => {
                    const tracksHtml = Object.keys(data.tracks).map(trackId => {
                        const track = data.tracks[trackId];
                        return `
                            <div class="mb-2 p-2 border rounded">
                                <strong>${track.name}</strong><br>
                                <small>${track.location} • ${track.length} • ${track.turns} turns</small>
                                <span class="status-active float-end">✓ ${track.status}</span>
                            </div>
                        `;
                    }).join('');
                    
                    document.getElementById('tracksList').innerHTML = tracksHtml;
                })
                .catch(error => {
                    document.getElementById('tracksList').innerHTML = '<div class="text-danger">Error loading tracks</div>';
                });
            
            function loadDemo() {
                fetch('/demo')
                    .then(response => response.json())
                    .then(data => {
                        const demoHtml = `
                            <div class="alert alert-success">
                                <h5>Demo Data Loaded: ${data.track_name}</h5>
                                <p><strong>Max Speed:</strong> ${data.analytics.max_speed} mph</p>
                                <p><strong>Max Braking:</strong> ${data.analytics.max_braking}%</p>
                                <p><strong>Max Lateral G:</strong> ${data.analytics.max_lateral_g}g</p>
                                <p><strong>Data Points:</strong> ${data.analytics.total_data_points}</p>
                            </div>
                        `;
                        document.getElementById('demoResults').innerHTML = demoHtml;
                    })
                    .catch(error => {
                        document.getElementById('demoResults').innerHTML = '<div class="alert alert-danger">Error loading demo data</div>';
                    });
            }
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=dashboard_html)