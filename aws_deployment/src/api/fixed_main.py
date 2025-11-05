"""
GR Cup Analytics API - Fixed Version with Real Data Integration
"""

import json
import boto3
from datetime import datetime
import os
import csv
from io import StringIO

def create_response(status_code, body, content_type='application/json'):
    """Create HTTP response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': content_type,
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(body) if content_type == 'application/json' else body
    }

def get_s3_data(bucket_name, key):
    """Get data from S3"""
    try:
        s3_client = boto3.client('s3')
        print(f"Attempting to get s3://{bucket_name}/{key}")
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        content = response['Body'].read().decode('utf-8')
        print(f"Successfully retrieved {len(content)} characters from S3")
        return content
    except s3_client.exceptions.NoSuchKey:
        print(f"File not found: s3://{bucket_name}/{key}")
        return None
    except Exception as e:
        print(f"Error getting S3 data from s3://{bucket_name}/{key}: {e}")
        import traceback
        traceback.print_exc()
        return None

def parse_csv_data(csv_content):
    """Parse CSV content and return analytics"""
    try:
        reader = csv.DictReader(StringIO(csv_content))
        data = list(reader)
        
        if not data:
            print("No data found in CSV")
            return None
        
        print(f"Loaded {len(data)} rows from CSV")
        
        # Calculate analytics from real telemetry data
        speeds = []
        braking = []
        throttle = []
        lateral_g = []
        laps = set()
        
        for row in data:
            try:
                if row.get('Speed'):
                    speeds.append(float(row['Speed']))
                if row.get('pbrake_f'):
                    braking.append(float(row['pbrake_f']))
                if row.get('ath'):
                    throttle.append(float(row['ath']))
                if row.get('accy_can'):
                    lateral_g.append(abs(float(row['accy_can'])))
                if row.get('lap'):
                    laps.add(row['lap'])
            except (ValueError, TypeError) as e:
                continue  # Skip invalid rows
        
        if not speeds:
            print("No valid speed data found")
            return None
        
        analytics = {
            'total_data_points': len(data),
            'max_speed': round(max(speeds), 1) if speeds else 0,
            'avg_speed': round(sum(speeds) / len(speeds), 1) if speeds else 0,
            'min_speed': round(min(speeds), 1) if speeds else 0,
            'max_braking': round(max(braking), 1) if braking else 0,
            'avg_throttle': round(sum(throttle) / len(throttle), 1) if throttle else 0,
            'max_lateral_g': round(max(lateral_g), 2) if lateral_g else 0,
            'unique_laps': len(laps),
            'track_name': data[0].get('track_name', 'Unknown') if data else 'Unknown'
        }
        
        print(f"Analytics calculated: {analytics}")
        return analytics
        
    except Exception as e:
        print(f"Error parsing CSV: {e}")
        import traceback
        traceback.print_exc()
        return None

def lambda_handler(event, context):
    """Main Lambda handler"""
    
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    
    # CORS preflight
    if method == 'OPTIONS':
        return create_response(200, {'message': 'CORS preflight'})
    
    # Root endpoint
    if path == '/' or path == '':
        return create_response(200, {
            "service": "GR Cup Analytics API",
            "version": "1.0.0",
            "status": "active",
            "message": "Welcome to GR Cup Analytics!",
            "endpoints": {
                "tracks": "/tracks",
                "analytics": "/analytics/{track_id}",
                "dashboard": "/dashboard",
                "health": "/health"
            }
        })
    
    # Health check
    elif path == '/health':
        return create_response(200, {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "gr-cup-analytics",
            "message": "All systems operational!"
        })
    
    # Tracks list
    elif path == '/tracks':
        tracks = {
            "BMP": {
                "name": "Barber Motorsports Park",
                "location": "Alabama, USA",
                "length": "2.38 miles",
                "turns": 17,
                "status": "active",
                "data_available": True
            },
            "COTA": {
                "name": "Circuit of the Americas",
                "location": "Texas, USA", 
                "length": "3.426 miles",
                "turns": 20,
                "status": "active",
                "data_available": True
            },
            "VIR": {
                "name": "Virginia International Raceway",
                "location": "Virginia, USA",
                "length": "3.27 miles", 
                "turns": 17,
                "status": "active",
                "data_available": True
            },
            "SEB": {
                "name": "Sebring International Raceway",
                "location": "Florida, USA",
                "length": "3.74 miles",
                "turns": 17,
                "status": "active",
                "data_available": True
            },
            "SON": {
                "name": "Sonoma Raceway",
                "location": "California, USA",
                "length": "2.52 miles",
                "turns": 12,
                "status": "active",
                "data_available": True
            },
            "RA": {
                "name": "Road America",
                "location": "Wisconsin, USA",
                "length": "4.048 miles",
                "turns": 14,
                "status": "active",
                "data_available": True
            },
            "INDY": {
                "name": "Indianapolis Motor Speedway",
                "location": "Indiana, USA",
                "length": "2.439 miles",
                "turns": 16,
                "status": "active",
                "data_available": True
            }
        }
        
        return create_response(200, {
            "tracks": tracks,
            "total_tracks": len(tracks),
            "message": "All GR Cup tracks available for analysis"
        })
    
    # Analytics for specific track
    elif path.startswith('/analytics/'):
        track_id = path.split('/')[-1].upper()
        
        # Try to get real data from S3 (this would be uploaded separately)
        bucket_name = f"gr-cup-data-dev-us-east-1-v2"
        key = f"processed-telemetry/{track_id}_telemetry_clean.csv"
        
        csv_data = get_s3_data(bucket_name, key)
        
        if csv_data:
            analytics = parse_csv_data(csv_data)
            if analytics:
                return create_response(200, {
                    "track_id": track_id,
                    "data_source": "real_telemetry",
                    "analytics": analytics
                })
        
        # Fallback to demo data if no real data available
        demo_analytics = {
            "BMP": {"max_speed": 158.0, "avg_speed": 125.5, "max_braking": 85.0, "max_lateral_g": 1.8, "total_data_points": 2500, "unique_laps": 5},
            "COTA": {"max_speed": 175.2, "avg_speed": 135.8, "max_braking": 92.0, "max_lateral_g": 2.1, "total_data_points": 2800, "unique_laps": 6},
            "VIR": {"max_speed": 165.5, "avg_speed": 130.2, "max_braking": 88.0, "max_lateral_g": 1.9, "total_data_points": 2600, "unique_laps": 5},
            "SEB": {"max_speed": 170.8, "avg_speed": 128.9, "max_braking": 90.0, "max_lateral_g": 2.0, "total_data_points": 2700, "unique_laps": 6},
            "SON": {"max_speed": 145.3, "avg_speed": 115.6, "max_braking": 95.0, "max_lateral_g": 2.3, "total_data_points": 2200, "unique_laps": 4},
            "RA": {"max_speed": 180.1, "avg_speed": 140.2, "max_braking": 85.0, "max_lateral_g": 1.7, "total_data_points": 3200, "unique_laps": 7},
            "INDY": {"max_speed": 172.5, "avg_speed": 132.8, "max_braking": 87.0, "max_lateral_g": 1.8, "total_data_points": 2900, "unique_laps": 6}
        }
        
        if track_id in demo_analytics:
            return create_response(200, {
                "track_id": track_id,
                "data_source": "demo_data",
                "analytics": demo_analytics[track_id]
            })
        else:
            return create_response(404, {"error": f"Track {track_id} not found"})
    
    # Dashboard
    elif path == '/dashboard':
        dashboard_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>GR Cup Analytics Dashboard</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
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
                .track-button {
                    margin: 5px;
                    min-width: 120px;
                }
            </style>
        </head>
        <body>
            <div class="container-fluid">
                <div class="dashboard-container">
                    <h1 class="header-title">GR Cup Analytics Dashboard</h1>
                    <p class="text-center lead">Real-time telemetry analysis for all 7 GR Cup tracks</p>
                    
                    <div class="row">
                        <div class="col-md-4">
                            <div class="track-card">
                                <h3>System Status</h3>
                                <div class="metric-badge">API: Online</div>
                                <div class="metric-badge">Tracks: 7 Active</div>
                                <div class="metric-badge">Data: Ready</div>
                            </div>
                            
                            <div class="track-card">
                                <h3>Track Selection</h3>
                                <div id="trackButtons"></div>
                            </div>
                            
                            <div class="track-card">
                                <h3>Quick Stats</h3>
                                <div id="quickStats">Select a track to view statistics</div>
                            </div>
                        </div>
                        
                        <div class="col-md-8">
                            <div class="track-card">
                                <h3>Performance Analytics</h3>
                                <div id="analyticsChart" style="height: 400px;"></div>
                            </div>
                            
                            <div class="track-card">
                                <h3>Track Comparison</h3>
                                <div id="comparisonChart" style="height: 300px;"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                let allTracksData = {};
                const apiUrl = window.location.origin + window.location.pathname.replace('/dashboard', '');
                
                // Load tracks and create buttons
                fetch(apiUrl + '/tracks')
                    .then(response => response.json())
                    .then(data => {
                        const buttonsHtml = Object.keys(data.tracks).map(trackId => {
                            const track = data.tracks[trackId];
                            return `<button class="btn btn-primary track-button" onclick="loadTrackData('${trackId}')">${trackId}</button>`;
                        }).join('');
                        
                        document.getElementById('trackButtons').innerHTML = buttonsHtml;
                        
                        // Load all track data for comparison
                        loadAllTracksData(Object.keys(data.tracks));
                    })
                    .catch(error => {
                        console.error('Error loading tracks:', error);
                    });
                
                function loadTrackData(trackId) {
                    fetch(apiUrl + '/analytics/' + trackId)
                        .then(response => response.json())
                        .then(data => {
                            updateQuickStats(data);
                            createAnalyticsChart(data);
                        })
                        .catch(error => {
                            console.error('Error loading track data:', error);
                        });
                }
                
                function loadAllTracksData(trackIds) {
                    Promise.all(trackIds.map(trackId => 
                        fetch(apiUrl + '/analytics/' + trackId).then(r => r.json())
                    )).then(results => {
                        results.forEach(data => {
                            allTracksData[data.track_id] = data.analytics;
                        });
                        createComparisonChart();
                    });
                }
                
                function updateQuickStats(data) {
                    const stats = data.analytics;
                    const dataSource = data.data_source === 'real_telemetry' ? 'Real Telemetry Data' : 'Demo Data';
                    const trackName = stats.track_name || data.track_id;
                    
                    const html = `
                        <div class="alert alert-${data.data_source === 'real_telemetry' ? 'success' : 'info'}">
                            <h5>${trackName}</h5>
                            <p><strong>Data Source:</strong> ${dataSource}</p>
                        </div>
                        <p><strong>Total Laps:</strong> ${stats.unique_laps}</p>
                        <p><strong>Max Speed:</strong> ${stats.max_speed} mph</p>
                        <p><strong>Avg Speed:</strong> ${stats.avg_speed} mph</p>
                        <p><strong>Max Braking:</strong> ${stats.max_braking}</p>
                        <p><strong>Max Lateral G:</strong> ${stats.max_lateral_g}g</p>
                        <p><strong>Data Points:</strong> ${stats.total_data_points.toLocaleString()}</p>
                    `;
                    document.getElementById('quickStats').innerHTML = html;
                }
                
                function createAnalyticsChart(data) {
                    const stats = data.analytics;
                    
                    const trace = {
                        x: ['Max Speed', 'Avg Speed', 'Max Braking', 'Max Lateral G', 'Avg Throttle'],
                        y: [stats.max_speed, stats.avg_speed, stats.max_braking, stats.max_lateral_g, stats.avg_throttle || 75],
                        type: 'bar',
                        marker: { color: ['#667eea', '#764ba2', '#ea4335', '#fbbc04', '#34a853'] }
                    };
                    
                    const layout = {
                        title: `${data.track_id} Performance Metrics`,
                        xaxis: { title: 'Metrics' },
                        yaxis: { title: 'Values' }
                    };
                    
                    Plotly.newPlot('analyticsChart', [trace], layout);
                }
                
                function createComparisonChart() {
                    const trackIds = Object.keys(allTracksData);
                    const maxSpeeds = trackIds.map(id => allTracksData[id].max_speed);
                    const avgSpeeds = trackIds.map(id => allTracksData[id].avg_speed);
                    
                    const trace1 = {
                        x: trackIds,
                        y: maxSpeeds,
                        type: 'bar',
                        name: 'Max Speed',
                        marker: { color: '#667eea' }
                    };
                    
                    const trace2 = {
                        x: trackIds,
                        y: avgSpeeds,
                        type: 'bar',
                        name: 'Avg Speed',
                        marker: { color: '#764ba2' }
                    };
                    
                    const layout = {
                        title: 'Speed Comparison Across All Tracks',
                        xaxis: { title: 'Tracks' },
                        yaxis: { title: 'Speed (mph)' },
                        barmode: 'group'
                    };
                    
                    Plotly.newPlot('comparisonChart', [trace1, trace2], layout);
                }
                
                // Load BMP data by default
                setTimeout(() => loadTrackData('BMP'), 1000);
            </script>
        </body>
        </html>
        """
        
        return create_response(200, dashboard_html, 'text/html')
    
    # 404 for unknown paths
    else:
        return create_response(404, {
            "error": "Not Found",
            "message": f"Path {path} not found",
            "available_endpoints": ["/", "/health", "/tracks", "/analytics/{track_id}", "/dashboard"]
        })