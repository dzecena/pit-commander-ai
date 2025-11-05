"""
GR Cup Analytics API - Judge/Stakeholder Dashboard with Clear Explanations
"""

import json
import boto3
from datetime import datetime
import os
import csv
from io import StringIO

d
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
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        content = response['Body'].read().decode('utf-8')
        return content
    except Exception as e:
        print(f"Error getting S3 data: {e}")
        return None

def parse_telemetry_data(csv_content):
    """Parse CSV and extract comprehensive analytics"""
    try:
        reader = csv.DictReader(StringIO(csv_content))
        data = list(reader)
        
        if not data:
            return None
        
        # Group data by driver/car
        drivers = {}
        
        for row in data:
            vehicle_id = row.get('vehicle_id', 'Unknown')
            chassis = row.get('chassis', 'Unknown')
            car_number = row.get('car_number', 'Unknown')
            
            driver_key = f"Driver #{car_number}"
            
            if driver_key not in drivers:
                drivers[driver_key] = {
                    'vehicle_id': vehicle_id,
                    'chassis': chassis,
                    'car_number': car_number,
                    'laps': set(),
                    'speeds': [],
                    'braking': [],
                    'throttle': [],
                    'lateral_g': [],
                    'steering': [],
                    'gear_data': [],
                    'rpm_data': [],
                    'sector_data': []
                }
            
            try:
                # Collect comprehensive data
                if row.get('Speed'):
                    drivers[driver_key]['speeds'].append(float(row['Speed']))
                if row.get('pbrake_f'):
                    drivers[driver_key]['braking'].append(float(row['pbrake_f']))
                if row.get('ath'):
                    drivers[driver_key]['throttle'].append(float(row['ath']))
                if row.get('accy_can'):
                    drivers[driver_key]['lateral_g'].append(abs(float(row['accy_can'])))
                if row.get('Steering_Angle'):
                    drivers[driver_key]['steering'].append(abs(float(row['Steering_Angle'])))
                if row.get('Gear'):
                    drivers[driver_key]['gear_data'].append(int(row['Gear']))
                if row.get('nmotor'):
                    drivers[driver_key]['rpm_data'].append(float(row['nmotor']))
                if row.get('lap'):
                    drivers[driver_key]['laps'].add(row['lap'])
                    
            except (ValueError, TypeError):
                continue
        
        # Calculate comprehensive analytics
        driver_analytics = {}
        all_speeds = []
        
        for driver_key, driver_data in drivers.items():
            if not driver_data['speeds']:
                continue
            
            all_speeds.extend(driver_data['speeds'])
            
            # Performance metrics
            max_speed = max(driver_data['speeds'])
            avg_speed = sum(driver_data['speeds']) / len(driver_data['speeds'])
            min_speed = min(driver_data['speeds'])
            
            # Gear usage analysis
            gear_usage = {}
            gear_efficiency = {}
            for gear in driver_data['gear_data']:
                gear_usage[gear] = gear_usage.get(gear, 0) + 1
            
            # Calculate gear efficiency (speed per gear)
            gear_speeds = {}
            for i, gear in enumerate(driver_data['gear_data']):
                if i < len(driver_data['speeds']):
                    if gear not in gear_speeds:
                        gear_speeds[gear] = []
                    gear_speeds[gear].append(driver_data['speeds'][i])
            
            for gear, speeds in gear_speeds.items():
                gear_efficiency[gear] = sum(speeds) / len(speeds) if speeds else 0
            
            analytics = {
                'vehicle_info': {
                    'vehicle_id': driver_data['vehicle_id'],
                    'chassis': driver_data['chassis'],
                    'car_number': driver_data['car_number']
                },
                'performance': {
                    'max_speed': round(max_speed, 1),
                    'avg_speed': round(avg_speed, 1),
                    'min_speed': round(min_speed, 1),
                    'speed_range': round(max_speed - min_speed, 1),
                    'consistency_score': round(100 - ((max_speed - min_speed) / max_speed * 100), 1)
                },
                'driving_metrics': {
                    'max_braking': round(max(driver_data['braking']), 1) if driver_data['braking'] else 0,
                    'avg_braking': round(sum(driver_data['braking']) / len(driver_data['braking']), 1) if driver_data['braking'] else 0,
                    'avg_throttle': round(sum(driver_data['throttle']) / len(driver_data['throttle']), 1) if driver_data['throttle'] else 0,
                    'max_lateral_g': round(max(driver_data['lateral_g']), 2) if driver_data['lateral_g'] else 0,
                    'avg_steering': round(sum(driver_data['steering']) / len(driver_data['steering']), 2) if driver_data['steering'] else 0,
                    'max_rpm': round(max(driver_data['rpm_data']), 0) if driver_data['rpm_data'] else 0,
                    'avg_rpm': round(sum(driver_data['rpm_data']) / len(driver_data['rpm_data']), 0) if driver_data['rpm_data'] else 0
                },
                'gear_analysis': {
                    'usage_count': gear_usage,
                    'efficiency': gear_efficiency,
                    'preferred_gear': max(gear_usage.items(), key=lambda x: x[1])[0] if gear_usage else 'N/A',
                    'gear_range': f"{min(gear_usage.keys())}-{max(gear_usage.keys())}" if gear_usage else 'N/A'
                },
                'session_data': {
                    'total_laps': len(driver_data['laps']),
                    'data_points': len(driver_data['speeds'])
                }
            }
            
            driver_analytics[driver_key] = analytics
        
        # Calculate track-wide statistics
        track_stats = {
            'fastest_driver': max(driver_analytics.items(), key=lambda x: x[1]['performance']['max_speed'])[0] if driver_analytics else 'N/A',
            'most_consistent': max(driver_analytics.items(), key=lambda x: x[1]['performance']['consistency_score'])[0] if driver_analytics else 'N/A',
            'track_record': max(all_speeds) if all_speeds else 0,
            'average_pace': sum(all_speeds) / len(all_speeds) if all_speeds else 0,
            'total_drivers': len(driver_analytics)
        }
        
        return {
            'drivers': driver_analytics,
            'track_stats': track_stats,
            'track_info': {
                'name': data[0].get('track_name', 'Unknown') if data else 'Unknown',
                'total_data_points': len(data)
            }
        }
        
    except Exception as e:
        print(f"Error parsing telemetry: {e}")
        return None

def lambda_handler(event, context):
    """Main Lambda handler with multiple dashboard pages"""
    
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return create_response(200, {'message': 'CORS preflight'})
    
    # API endpoints
    if path == '/' or path == '':
        return create_response(200, {
            "service": "GR Cup Judge Dashboard System",
            "version": "3.0.0",
            "pages": {
                "main_dashboard": "/dashboard",
                "driver_comparison": "/compare",
                "track_summary": "/summary",
                "technical_analysis": "/technical"
            }
        })
    
    elif path == '/tracks':
        tracks = {
            "BMP": {"name": "Barber Motorsports Park", "location": "Alabama, USA", "length": "2.38 miles", "turns": 17},
            "COTA": {"name": "Circuit of the Americas", "location": "Texas, USA", "length": "3.426 miles", "turns": 20},
            "VIR": {"name": "Virginia International Raceway", "location": "Virginia, USA", "length": "3.27 miles", "turns": 17},
            "SEB": {"name": "Sebring International Raceway", "location": "Florida, USA", "length": "3.74 miles", "turns": 17},
            "SON": {"name": "Sonoma Raceway", "location": "California, USA", "length": "2.52 miles", "turns": 12},
            "RA": {"name": "Road America", "location": "Wisconsin, USA", "length": "4.048 miles", "turns": 14},
            "INDY": {"name": "Indianapolis Motor Speedway", "location": "Indiana, USA", "length": "2.439 miles", "turns": 16}
        }
        return create_response(200, {"tracks": tracks})
    
    elif path.startswith('/data/'):
        track_id = path.split('/')[-1].upper()
        bucket_name = "gr-cup-data-dev-us-east-1-v2"
        key = f"processed-telemetry/{track_id}_telemetry_clean.csv"
        
        csv_data = get_s3_data(bucket_name, key)
        if csv_data:
            telemetry_data = parse_telemetry_data(csv_data)
            if telemetry_data:
                return create_response(200, {
                    "track_id": track_id,
                    "data": telemetry_data
                })
        
        return create_response(404, {"error": f"No data found for track {track_id}"})
    
    # Dashboard pages
    elif path == '/dashboard':
        return create_response(200, get_main_dashboard(), 'text/html')
    
    elif path == '/compare':
        return create_response(200, get_comparison_dashboard(), 'text/html')
    
    elif path == '/summary':
        return create_response(200, get_summary_dashboard(), 'text/html')
    
    elif path == '/technical':
        return create_response(200, get_technical_dashboard(), 'text/html')
    
    else:
        return create_response(404, {"error": "Page not found"})

def get_main_dashboard():
    """Main dashboard page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>GR Cup Judge Dashboard - Main</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .dashboard-container { background: rgba(255,255,255,0.95); border-radius: 15px; margin: 20px; padding: 30px; }
            .nav-pills .nav-link { margin: 0 5px; }
            .nav-pills .nav-link.active { background: linear-gradient(45deg, #667eea, #764ba2); }
            .card { border-radius: 10px; margin: 10px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        </style>
    </head>
    <body>
        <div class="container-fluid">
            <div class="dashboard-container">
                <h1 class="text-center mb-4">GR Cup Judge Dashboard System</h1>
                
                <!-- Navigation -->
                <ul class="nav nav-pills justify-content-center mb-4">
                    <li class="nav-item"><a class="nav-link active" href="/dashboard">Main Dashboard</a></li>
                    <li class="nav-item"><a class="nav-link" href="/compare">Driver Comparison</a></li>
                    <li class="nav-item"><a class="nav-link" href="/summary">Track Summary</a></li>
                    <li class="nav-item"><a class="nav-link" href="/technical">Technical Analysis</a></li>
                </ul>
                
                <div class="row">
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-body">
                                <h5>Track Selection</h5>
                                <select id="trackSelect" class="form-select mb-2">
                                    <option value="">Select Track...</option>
                                </select>
                                <button id="loadData" class="btn btn-primary w-100">Load Track Data</button>
                            </div>
                        </div>
                        
                        <div class="card">
                            <div class="card-body">
                                <h5>Track Overview</h5>
                                <div id="trackOverview">Select a track to view overview</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body">
                                <h5>Driver Performance Overview</h5>
                                <div id="performanceChart" style="height: 400px;"></div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-body">
                                <h5>Top Performers</h5>
                                <div id="topPerformers">Load track data to see rankings</div>
                            </div>
                        </div>
                        
                        <div class="card">
                            <div class="card-body">
                                <h5>Quick Stats</h5>
                                <div id="quickStats">Load track data to see statistics</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            const apiUrl = window.location.origin + window.location.pathname.replace('/dashboard', '');
            let currentTrackData = null;
            
            // Load tracks
            fetch(apiUrl + '/tracks')
                .then(response => response.json())
                .then(data => {
                    const select = document.getElementById('trackSelect');
                    Object.keys(data.tracks).forEach(trackId => {
                        const track = data.tracks[trackId];
                        select.innerHTML += `<option value="${trackId}">${track.name}</option>`;
                    });
                });
            
            document.getElementById('loadData').addEventListener('click', function() {
                const trackId = document.getElementById('trackSelect').value;
                if (trackId) loadTrackData(trackId);
            });
            
            function loadTrackData(trackId) {
                fetch(apiUrl + '/data/' + trackId)
                    .then(response => response.json())
                    .then(data => {
                        currentTrackData = data;
                        updateDashboard(data);
                    })
                    .catch(error => console.error('Error:', error));
            }
            
            function updateDashboard(data) {
                const trackData = data.data;
                
                // Track overview
                document.getElementById('trackOverview').innerHTML = `
                    <p><strong>Track:</strong> ${trackData.track_info.name}</p>
                    <p><strong>Total Drivers:</strong> ${trackData.track_stats.total_drivers}</p>
                    <p><strong>Data Points:</strong> ${trackData.track_info.total_data_points.toLocaleString()}</p>
                    <p><strong>Track Record:</strong> ${trackData.track_stats.track_record.toFixed(1)} mph</p>
                `;
                
                // Top performers
                document.getElementById('topPerformers').innerHTML = `
                    <div class="mb-2">
                        <strong>Fastest Driver:</strong><br>
                        ${trackData.track_stats.fastest_driver}
                    </div>
                    <div class="mb-2">
                        <strong>Most Consistent:</strong><br>
                        ${trackData.track_stats.most_consistent}
                    </div>
                `;
                
                // Quick stats
                document.getElementById('quickStats').innerHTML = `
                    <p><strong>Average Pace:</strong> ${trackData.track_stats.average_pace.toFixed(1)} mph</p>
                    <p><strong>Speed Range:</strong> ${(trackData.track_stats.track_record - Math.min(...Object.values(trackData.drivers).map(d => d.performance.min_speed))).toFixed(1)} mph</p>
                `;
                
                // Performance chart
                createPerformanceChart(trackData.drivers);
            }
            
            function createPerformanceChart(drivers) {
                const driverNames = Object.keys(drivers);
                const maxSpeeds = driverNames.map(name => drivers[name].performance.max_speed);
                const avgSpeeds = driverNames.map(name => drivers[name].performance.avg_speed);
                const consistency = driverNames.map(name => drivers[name].performance.consistency_score);
                
                const trace1 = {
                    x: driverNames,
                    y: maxSpeeds,
                    type: 'bar',
                    name: 'Max Speed (mph)',
                    marker: { color: '#667eea' }
                };
                
                const trace2 = {
                    x: driverNames,
                    y: avgSpeeds,
                    type: 'bar',
                    name: 'Avg Speed (mph)',
                    marker: { color: '#764ba2' }
                };
                
                const layout = {
                    title: 'Driver Performance Comparison',
                    xaxis: { title: 'Drivers' },
                    yaxis: { title: 'Speed (mph)' },
                    barmode: 'group'
                };
                
                Plotly.newPlot('performanceChart', [trace1, trace2], layout);
            }
        </script>
    </body>
    </html>
    """