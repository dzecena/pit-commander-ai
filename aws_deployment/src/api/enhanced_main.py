"""
GR Cup Analytics API - Enhanced Version with Driver/Car Analysis
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
    except Exception as e:
        print(f"Error getting S3 data: {e}")
        return None

def parse_telemetry_data(csv_content):
    """Parse CSV and extract driver/car specific analytics"""
    try:
        reader = csv.DictReader(StringIO(csv_content))
        data = list(reader)
        
        if not data:
            return None
        
        # Group data by driver/car
        drivers = {}
        all_data = []
        
        for row in data:
            vehicle_id = row.get('vehicle_id', 'Unknown')
            chassis = row.get('chassis', 'Unknown')
            car_number = row.get('car_number', 'Unknown')
            
            driver_key = f"{vehicle_id} (Car #{car_number})"
            
            if driver_key not in drivers:
                drivers[driver_key] = {
                    'vehicle_id': vehicle_id,
                    'chassis': chassis,
                    'car_number': car_number,
                    'laps': set(),
                    'data_points': 0,
                    'speeds': [],
                    'braking': [],
                    'throttle': [],
                    'lateral_g': [],
                    'steering': [],
                    'gear_usage': {},
                    'sector_times': {}
                }
            
            try:
                # Collect data for this driver
                if row.get('Speed'):
                    speed = float(row['Speed'])
                    drivers[driver_key]['speeds'].append(speed)
                    all_data.append(speed)
                
                if row.get('pbrake_f'):
                    drivers[driver_key]['braking'].append(float(row['pbrake_f']))
                
                if row.get('ath'):
                    drivers[driver_key]['throttle'].append(float(row['ath']))
                
                if row.get('accy_can'):
                    drivers[driver_key]['lateral_g'].append(abs(float(row['accy_can'])))
                
                if row.get('Steering_Angle'):
                    drivers[driver_key]['steering'].append(abs(float(row['Steering_Angle'])))
                
                if row.get('Gear'):
                    gear = row['Gear']
                    if gear not in drivers[driver_key]['gear_usage']:
                        drivers[driver_key]['gear_usage'][gear] = 0
                    drivers[driver_key]['gear_usage'][gear] += 1
                
                if row.get('lap'):
                    drivers[driver_key]['laps'].add(row['lap'])
                
                drivers[driver_key]['data_points'] += 1
                
            except (ValueError, TypeError):
                continue
        
        # Calculate analytics for each driver
        driver_analytics = {}
        for driver_key, driver_data in drivers.items():
            if not driver_data['speeds']:
                continue
                
            analytics = {
                'vehicle_info': {
                    'vehicle_id': driver_data['vehicle_id'],
                    'chassis': driver_data['chassis'],
                    'car_number': driver_data['car_number']
                },
                'performance': {
                    'max_speed': round(max(driver_data['speeds']), 1),
                    'avg_speed': round(sum(driver_data['speeds']) / len(driver_data['speeds']), 1),
                    'min_speed': round(min(driver_data['speeds']), 1),
                    'speed_consistency': round(100 - (max(driver_data['speeds']) - min(driver_data['speeds'])) / max(driver_data['speeds']) * 100, 1)
                },
                'driving_style': {
                    'max_braking': round(max(driver_data['braking']), 1) if driver_data['braking'] else 0,
                    'avg_throttle': round(sum(driver_data['throttle']) / len(driver_data['throttle']), 1) if driver_data['throttle'] else 0,
                    'max_lateral_g': round(max(driver_data['lateral_g']), 2) if driver_data['lateral_g'] else 0,
                    'avg_steering_input': round(sum(driver_data['steering']) / len(driver_data['steering']), 2) if driver_data['steering'] else 0
                },
                'session_data': {
                    'total_laps': len(driver_data['laps']),
                    'data_points': driver_data['data_points'],
                    'gear_usage': driver_data['gear_usage']
                },
                'sector_analysis': analyze_sector_performance(driver_data, data)
            }
            
            # Generate performance insights
            analytics['insights'] = generate_performance_insights(analytics, all_data)
            
            driver_analytics[driver_key] = analytics
        
        return {
            'drivers': driver_analytics,
            'track_summary': {
                'total_drivers': len(driver_analytics),
                'total_data_points': len(data),
                'track_name': data[0].get('track_name', 'Unknown') if data else 'Unknown'
            }
        }
        
    except Exception as e:
        print(f"Error parsing telemetry: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_performance_insights(driver_analytics, all_speeds):
    """Generate performance insights and recommendations"""
    insights = []
    
    performance = driver_analytics['performance']
    driving_style = driver_analytics['driving_style']
    
    # Speed analysis
    if all_speeds:
        track_avg_speed = sum(all_speeds) / len(all_speeds)
        speed_percentile = (len([s for s in all_speeds if s < performance['avg_speed']]) / len(all_speeds)) * 100
        
        if speed_percentile > 75:
            insights.append({
                'type': 'positive',
                'category': 'Speed',
                'message': f"Excellent pace! You're faster than {speed_percentile:.0f}% of drivers on track."
            })
        elif speed_percentile < 25:
            insights.append({
                'type': 'improvement',
                'category': 'Speed',
                'message': f"Focus on increasing pace. You're {track_avg_speed - performance['avg_speed']:.1f} mph below track average."
            })
    
    # Consistency analysis
    if performance['speed_consistency'] > 85:
        insights.append({
            'type': 'positive',
            'category': 'Consistency',
            'message': f"Great consistency! {performance['speed_consistency']:.1f}% speed consistency shows good control."
        })
    elif performance['speed_consistency'] < 70:
        insights.append({
            'type': 'improvement',
            'category': 'Consistency',
            'message': "Work on consistency. Large speed variations suggest setup or driving technique issues."
        })
    
    # Braking analysis
    if driving_style['max_braking'] > 90:
        insights.append({
            'type': 'warning',
            'category': 'Braking',
            'message': "Very aggressive braking detected. Consider earlier, smoother brake application."
        })
    elif driving_style['max_braking'] < 50:
        insights.append({
            'type': 'improvement',
            'category': 'Braking',
            'message': "Low braking intensity. You may be leaving time on the table - brake harder into corners."
        })
    
    # Throttle analysis
    if driving_style['avg_throttle'] > 80:
        insights.append({
            'type': 'positive',
            'category': 'Throttle',
            'message': f"Good throttle usage at {driving_style['avg_throttle']:.1f}% average. Maximizing power delivery."
        })
    elif driving_style['avg_throttle'] < 60:
        insights.append({
            'type': 'improvement',
            'category': 'Throttle',
            'message': "Conservative throttle application. Work on getting on power earlier out of corners."
        })
    
    # G-force analysis
    if driving_style['max_lateral_g'] > 1.5:
        insights.append({
            'type': 'positive',
            'category': 'Cornering',
            'message': f"High cornering forces ({driving_style['max_lateral_g']:.2f}g) show you're pushing the limits."
        })
    
    # Steering analysis
    if driving_style['avg_steering_input'] > 10:
        insights.append({
            'type': 'improvement',
            'category': 'Steering',
            'message': "High steering input suggests overdriving. Focus on smoother, more precise inputs."
        })
    
    # Gear usage analysis
    session_data = driver_analytics['session_data']
    if 'gear_usage' in session_data and session_data['gear_usage']:
        gear_insights = analyze_gear_usage(session_data['gear_usage'], session_data['total_laps'])
        insights.extend(gear_insights)
    
    return insights

def analyze_gear_usage(gear_usage, total_laps):
    """Analyze gear usage patterns and provide insights"""
    gear_insights = []
    
    # Calculate gear distribution
    total_shifts = sum(gear_usage.values())
    gear_percentages = {gear: (count / total_shifts * 100) for gear, count in gear_usage.items()}
    
    # Most used gear
    most_used_gear = max(gear_usage.items(), key=lambda x: x[1])
    
    # Gear range analysis
    gears_used = [int(gear) for gear in gear_usage.keys() if gear.isdigit()]
    if gears_used:
        min_gear = min(gears_used)
        max_gear = max(gears_used)
        gear_range = max_gear - min_gear + 1
        
        # High gear usage (5th/6th gear)
        high_gear_usage = sum(count for gear, count in gear_usage.items() 
                             if gear.isdigit() and int(gear) >= 5)
        high_gear_percentage = (high_gear_usage / total_shifts * 100) if total_shifts > 0 else 0
        
        # Low gear usage (1st/2nd gear)
        low_gear_usage = sum(count for gear, count in gear_usage.items() 
                            if gear.isdigit() and int(gear) <= 2)
        low_gear_percentage = (low_gear_usage / total_shifts * 100) if total_shifts > 0 else 0
        
        # Generate insights based on gear patterns
        if high_gear_percentage > 60:
            gear_insights.append({
                'type': 'positive',
                'category': 'Gear Usage',
                'message': f"Excellent top-end usage! {high_gear_percentage:.1f}% in high gears shows good straight-line speed."
            })
        elif high_gear_percentage < 30:
            gear_insights.append({
                'type': 'improvement',
                'category': 'Gear Usage',
                'message': f"Low high-gear usage ({high_gear_percentage:.1f}%). Focus on carrying more speed through corners."
            })
        
        if low_gear_usage > total_shifts * 0.3:
            gear_insights.append({
                'type': 'warning',
                'category': 'Gear Usage',
                'message': f"High low-gear usage ({low_gear_percentage:.1f}%). May indicate over-braking or poor corner exit."
            })
        
        if gear_range >= 5:
            gear_insights.append({
                'type': 'positive',
                'category': 'Gear Usage',
                'message': f"Good gear range utilization (Gears {min_gear}-{max_gear}). Using full transmission effectively."
            })
        
        # Most used gear analysis
        if most_used_gear[0].isdigit():
            gear_num = int(most_used_gear[0])
            gear_percent = gear_percentages[most_used_gear[0]]
            
            if gear_num == 3 and gear_percent > 40:
                gear_insights.append({
                    'type': 'improvement',
                    'category': 'Gear Usage',
                    'message': f"Heavy 3rd gear usage ({gear_percent:.1f}%). Work on corner exit speed to reach higher gears sooner."
                })
            elif gear_num >= 5 and gear_percent > 35:
                gear_insights.append({
                    'type': 'positive',
                    'category': 'Gear Usage',
                    'message': f"Strong {gear_num}th gear usage ({gear_percent:.1f}%). Good high-speed sections and corner exits."
                })
    
    return gear_insights

def analyze_sector_performance(driver_data, all_data):
    """Analyze performance by track sectors with baseline comparison"""
    
    # Group data by sectors (S1, S2, S3) - we'll estimate based on lap progress
    sector_data = {'S1': [], 'S2': [], 'S3': []}
    
    # Process all data to create sector baselines
    all_sector_data = {'S1': [], 'S2': [], 'S3': []}
    
    for row in all_data:
        try:
            # Estimate sector based on lap progress or use existing sector data
            if 'sector' in row and row['sector']:
                sector = row['sector']
            else:
                # Estimate sector based on data position in lap (simplified)
                # In real implementation, you'd use timing beacons or GPS coordinates
                lap_position = hash(row.get('timestamp', '')) % 3
                sector = ['S1', 'S2', 'S3'][lap_position]
            
            speed = float(row.get('Speed', 0)) if row.get('Speed') else 0
            braking = float(row.get('pbrake_f', 0)) if row.get('pbrake_f') else 0
            throttle = float(row.get('ath', 0)) if row.get('ath') else 0
            lateral_g = abs(float(row.get('accy_can', 0))) if row.get('accy_can') else 0
            
            sector_point = {
                'speed': speed,
                'braking': braking,
                'throttle': throttle,
                'lateral_g': lateral_g
            }
            
            # Add to all drivers baseline
            if speed > 0:  # Valid data point
                all_sector_data[sector].append(sector_point)
            
            # Add to this driver's data if it's their data
            vehicle_id = row.get('vehicle_id', '')
            if vehicle_id == driver_data['vehicle_id']:
                sector_data[sector].append(sector_point)
                
        except (ValueError, TypeError, KeyError):
            continue
    
    # Calculate sector performance metrics
    sector_analysis = {}
    
    for sector in ['S1', 'S2', 'S3']:
        driver_sector = sector_data[sector]
        baseline_sector = all_sector_data[sector]
        
        if not driver_sector or not baseline_sector:
            continue
            
        # Driver sector averages
        driver_avg_speed = sum(p['speed'] for p in driver_sector) / len(driver_sector)
        driver_avg_braking = sum(p['braking'] for p in driver_sector) / len(driver_sector)
        driver_avg_throttle = sum(p['throttle'] for p in driver_sector) / len(driver_sector)
        driver_max_lateral_g = max(p['lateral_g'] for p in driver_sector)
        
        # Baseline averages (all drivers)
        baseline_avg_speed = sum(p['speed'] for p in baseline_sector) / len(baseline_sector)
        baseline_avg_braking = sum(p['braking'] for p in baseline_sector) / len(baseline_sector)
        baseline_avg_throttle = sum(p['throttle'] for p in baseline_sector) / len(baseline_sector)
        baseline_max_lateral_g = max(p['lateral_g'] for p in baseline_sector)
        
        # Calculate performance vs baseline
        speed_vs_baseline = ((driver_avg_speed - baseline_avg_speed) / baseline_avg_speed * 100) if baseline_avg_speed > 0 else 0
        braking_vs_baseline = ((driver_avg_braking - baseline_avg_braking) / baseline_avg_braking * 100) if baseline_avg_braking > 0 else 0
        throttle_vs_baseline = ((driver_avg_throttle - baseline_avg_throttle) / baseline_avg_throttle * 100) if baseline_avg_throttle > 0 else 0
        lateral_g_vs_baseline = ((driver_max_lateral_g - baseline_max_lateral_g) / baseline_max_lateral_g * 100) if baseline_max_lateral_g > 0 else 0
        
        # Determine sector strengths and weaknesses
        strengths = []
        weaknesses = []
        improvements = []
        
        if speed_vs_baseline > 5:
            strengths.append(f"Speed advantage: +{speed_vs_baseline:.1f}% vs field")
        elif speed_vs_baseline < -5:
            weaknesses.append(f"Speed deficit: {speed_vs_baseline:.1f}% vs field")
            improvements.append("Focus on carrying more speed through this sector")
        
        if lateral_g_vs_baseline > 10:
            strengths.append(f"Strong cornering: +{lateral_g_vs_baseline:.1f}% lateral G")
        elif lateral_g_vs_baseline < -10:
            weaknesses.append(f"Conservative cornering: {lateral_g_vs_baseline:.1f}% lateral G")
            improvements.append("Push harder through corners - more grip available")
        
        if throttle_vs_baseline > 10:
            strengths.append(f"Aggressive throttle: +{throttle_vs_baseline:.1f}% vs field")
        elif throttle_vs_baseline < -10:
            weaknesses.append("Conservative throttle application")
            improvements.append("Get on throttle earlier and more aggressively")
        
        if braking_vs_baseline > 20:
            weaknesses.append("Over-braking detected")
            improvements.append("Brake later and release sooner")
        elif braking_vs_baseline < -20:
            improvements.append("Could brake harder - leaving time on table")
        
        sector_analysis[sector] = {
            'driver_metrics': {
                'avg_speed': round(driver_avg_speed, 1),
                'avg_braking': round(driver_avg_braking, 1),
                'avg_throttle': round(driver_avg_throttle, 1),
                'max_lateral_g': round(driver_max_lateral_g, 2)
            },
            'baseline_comparison': {
                'speed_vs_baseline': round(speed_vs_baseline, 1),
                'braking_vs_baseline': round(braking_vs_baseline, 1),
                'throttle_vs_baseline': round(throttle_vs_baseline, 1),
                'lateral_g_vs_baseline': round(lateral_g_vs_baseline, 1)
            },
            'performance_rating': calculate_sector_rating(speed_vs_baseline, lateral_g_vs_baseline, throttle_vs_baseline),
            'strengths': strengths,
            'weaknesses': weaknesses,
            'improvements': improvements,
            'data_points': len(driver_sector)
        }
    
    return sector_analysis

def calculate_sector_rating(speed_diff, lateral_g_diff, throttle_diff):
    """Calculate overall sector performance rating"""
    
    # Weight the different factors
    speed_weight = 0.5
    lateral_g_weight = 0.3
    throttle_weight = 0.2
    
    # Normalize to 0-100 scale
    speed_score = max(0, min(100, 50 + speed_diff * 2))
    lateral_g_score = max(0, min(100, 50 + lateral_g_diff))
    throttle_score = max(0, min(100, 50 + throttle_diff))
    
    overall_score = (speed_score * speed_weight + 
                    lateral_g_score * lateral_g_weight + 
                    throttle_score * throttle_weight)
    
    if overall_score >= 80:
        return {'score': round(overall_score, 1), 'grade': 'A', 'description': 'Excellent'}
    elif overall_score >= 70:
        return {'score': round(overall_score, 1), 'grade': 'B', 'description': 'Good'}
    elif overall_score >= 60:
        return {'score': round(overall_score, 1), 'grade': 'C', 'description': 'Average'}
    elif overall_score >= 50:
        return {'score': round(overall_score, 1), 'grade': 'D', 'description': 'Below Average'}
    else:
        return {'score': round(overall_score, 1), 'grade': 'F', 'description': 'Needs Work'}

def lambda_handler(event, context):
    """Main Lambda handler"""
    
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return create_response(200, {'message': 'CORS preflight'})
    
    if path == '/' or path == '':
        return create_response(200, {
            "service": "GR Cup Analytics API - Enhanced",
            "version": "2.0.0",
            "status": "active",
            "message": "Welcome to GR Cup Analytics with Driver Insights!",
            "endpoints": {
                "tracks": "/tracks",
                "analytics": "/analytics/{track_id}",
                "drivers": "/drivers/{track_id}",
                "dashboard": "/dashboard",
                "health": "/health"
            }
        })
    
    elif path == '/health':
        return create_response(200, {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "gr-cup-analytics-enhanced"
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
        return create_response(200, {"tracks": tracks, "total_tracks": len(tracks)})
    
    elif path.startswith('/analytics/') or path.startswith('/drivers/'):
        track_id = path.split('/')[-1].upper()
        bucket_name = "gr-cup-data-dev-us-east-1-v2"
        key = f"processed-telemetry/{track_id}_telemetry_clean.csv"
        
        csv_data = get_s3_data(bucket_name, key)
        
        if csv_data:
            telemetry_data = parse_telemetry_data(csv_data)
            if telemetry_data:
                return create_response(200, {
                    "track_id": track_id,
                    "data_source": "real_telemetry",
                    "telemetry_data": telemetry_data
                })
        
        return create_response(404, {"error": f"No telemetry data found for track {track_id}"})
    
    elif path == '/dashboard':
        dashboard_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>GR Cup Analytics - Driver Performance Dashboard</title>
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
                .card { 
                    border-radius: 10px;
                    margin: 10px 0;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    transition: transform 0.2s;
                }
                .card:hover { 
                    transform: translateY(-2px);
                    box-shadow: 0 8px 15px rgba(0,0,0,0.2);
                }
                .insight-positive { border-left: 4px solid #28a745; }
                .insight-improvement { border-left: 4px solid #ffc107; }
                .insight-warning { border-left: 4px solid #dc3545; }
                .metric-badge {
                    background: linear-gradient(45deg, #667eea, #764ba2);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    display: inline-block;
                    margin: 3px;
                    font-size: 0.9em;
                }
            </style>
        </head>
        <body>
            <div class="container-fluid">
                <div class="dashboard-container">
                    <h1 class="text-center mb-4">GR Cup Driver Performance Dashboard</h1>
                    
                    <div class="row">
                        <div class="col-md-3">
                            <div class="card">
                                <div class="card-body">
                                    <h5>Track Selection</h5>
                                    <select id="trackSelect" class="form-select mb-2">
                                        <option value="">Select Track...</option>
                                    </select>
                                    <button id="loadTrack" class="btn btn-primary w-100">Load Data</button>
                                </div>
                            </div>
                            
                            <div class="card">
                                <div class="card-body">
                                    <h5>Driver/Car Selection</h5>
                                    <select id="driverSelect" class="form-select mb-2">
                                        <option value="">Select Driver...</option>
                                    </select>
                                    <div id="vehicleInfo" class="mt-2"></div>
                                </div>
                            </div>
                            
                            <div class="card">
                                <div class="card-body">
                                    <h5>Performance Metrics</h5>
                                    <div id="performanceMetrics">Select a driver to view metrics</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-body">
                                    <h5>Performance Analysis</h5>
                                    <div id="performanceChart" style="height: 400px;"></div>
                                </div>
                            </div>
                            
                            <div class="card">
                                <div class="card-body">
                                    <h5>Driver Speed Comparison</h5>
                                    <div id="comparisonChart" style="height: 300px;"></div>
                                </div>
                            </div>
                            
                            <div class="card">
                                <div class="card-body">
                                    <h5>Gear Usage Comparison</h5>
                                    <div id="gearComparisonChart" style="height: 350px;"></div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-3">
                            <div class="card">
                                <div class="card-body">
                                    <h5>Sector Performance Analysis</h5>
                                    <div id="sectorAnalysis">Select a driver to see sector breakdown</div>
                                </div>
                            </div>
                            
                            <div class="card">
                                <div class="card-body">
                                    <h5>Performance Insights</h5>
                                    <div id="insights">Select a driver to see insights</div>
                                </div>
                            </div>
                            
                            <div class="card">
                                <div class="card-body">
                                    <h5>Gear Usage Analysis</h5>
                                    <div id="gearUsage"></div>
                                    <div id="gearChart" style="height: 200px;"></div>
                                    <div id="gearInsights" class="mt-2"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                let currentTrackData = null;
                const apiUrl = window.location.origin + window.location.pathname.replace('/dashboard', '');
                
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
                
                document.getElementById('loadTrack').addEventListener('click', function() {
                    const trackId = document.getElementById('trackSelect').value;
                    if (trackId) loadTrackData(trackId);
                });
                
                document.getElementById('driverSelect').addEventListener('change', function() {
                    const driverId = this.value;
                    if (driverId && currentTrackData) {
                        showDriverData(currentTrackData.telemetry_data.drivers[driverId], driverId);
                    }
                });
                
                function loadTrackData(trackId) {
                    fetch(apiUrl + '/drivers/' + trackId)
                        .then(response => response.json())
                        .then(data => {
                            currentTrackData = data;
                            populateDriverSelect(data.telemetry_data.drivers);
                            createDriverComparison(data.telemetry_data.drivers);
                        })
                        .catch(error => console.error('Error:', error));
                }
                
                function populateDriverSelect(drivers) {
                    const select = document.getElementById('driverSelect');
                    select.innerHTML = '<option value="">Select Driver...</option>';
                    
                    Object.keys(drivers).forEach(driverId => {
                        select.innerHTML += `<option value="${driverId}">${driverId}</option>`;
                    });
                }
                
                function showDriverData(driverData, driverId) {
                    // Vehicle info
                    const vehicleInfo = `
                        <div class="metric-badge">Car #${driverData.vehicle_info.car_number}</div>
                        <div class="metric-badge">Chassis: ${driverData.vehicle_info.chassis}</div>
                    `;
                    document.getElementById('vehicleInfo').innerHTML = vehicleInfo;
                    
                    // Performance metrics
                    const metrics = `
                        <p><strong>Max Speed:</strong> ${driverData.performance.max_speed} mph</p>
                        <p><strong>Avg Speed:</strong> ${driverData.performance.avg_speed} mph</p>
                        <p><strong>Consistency:</strong> ${driverData.performance.speed_consistency}%</p>
                        <p><strong>Max Braking:</strong> ${driverData.driving_style.max_braking}</p>
                        <p><strong>Avg Throttle:</strong> ${driverData.driving_style.avg_throttle}%</p>
                        <p><strong>Max Lateral G:</strong> ${driverData.driving_style.max_lateral_g}g</p>
                        <p><strong>Total Laps:</strong> ${driverData.session_data.total_laps}</p>
                    `;
                    document.getElementById('performanceMetrics').innerHTML = metrics;
                    
                    // Insights
                    const insightsHtml = driverData.insights.map(insight => `
                        <div class="alert alert-sm insight-${insight.type} mb-2">
                            <strong>${insight.category}:</strong> ${insight.message}
                        </div>
                    `).join('');
                    document.getElementById('insights').innerHTML = insightsHtml || 'No specific insights available.';
                    
                    // Sector analysis
                    showSectorAnalysis(driverData.sector_analysis);
                    
                    // Gear usage analysis
                    showGearAnalysis(driverData.session_data.gear_usage, driverData.insights);
                    
                    // Performance chart
                    createPerformanceChart(driverData, driverId);
                }
                
                function createPerformanceChart(driverData, driverId) {
                    const trace = {
                        x: ['Max Speed', 'Avg Speed', 'Consistency', 'Max Braking', 'Avg Throttle', 'Max Lateral G'],
                        y: [
                            driverData.performance.max_speed,
                            driverData.performance.avg_speed,
                            driverData.performance.speed_consistency,
                            driverData.driving_style.max_braking,
                            driverData.driving_style.avg_throttle,
                            driverData.driving_style.max_lateral_g * 50  // Scale for visibility
                        ],
                        type: 'bar',
                        marker: { color: ['#667eea', '#764ba2', '#28a745', '#dc3545', '#ffc107', '#17a2b8'] }
                    };
                    
                    const layout = {
                        title: `${driverId} Performance Profile`,
                        xaxis: { title: 'Metrics' },
                        yaxis: { title: 'Values' }
                    };
                    
                    Plotly.newPlot('performanceChart', [trace], layout);
                }
                
                function createDriverComparison(drivers) {
                    const driverIds = Object.keys(drivers);
                    const maxSpeeds = driverIds.map(id => drivers[id].performance.max_speed);
                    const avgSpeeds = driverIds.map(id => drivers[id].performance.avg_speed);
                    
                    const trace1 = {
                        x: driverIds.map(id => id.split(' ')[0]), // Shortened names
                        y: maxSpeeds,
                        type: 'bar',
                        name: 'Max Speed',
                        marker: { color: '#667eea' }
                    };
                    
                    const trace2 = {
                        x: driverIds.map(id => id.split(' ')[0]),
                        y: avgSpeeds,
                        type: 'bar',
                        name: 'Avg Speed',
                        marker: { color: '#764ba2' }
                    };
                    
                    const layout = {
                        title: 'Driver Speed Comparison',
                        xaxis: { title: 'Drivers' },
                        yaxis: { title: 'Speed (mph)' },
                        barmode: 'group'
                    };
                    
                    Plotly.newPlot('comparisonChart', [trace1, trace2], layout);
                    
                    // Create gear comparison chart
                    createGearComparison(drivers);
                }
                
                function createGearComparison(drivers) {
                    const driverIds = Object.keys(drivers);
                    
                    if (driverIds.length === 0) return;
                    
                    // Get all unique gears across all drivers
                    const allGears = new Set();
                    Object.values(drivers).forEach(driver => {
                        Object.keys(driver.session_data.gear_usage).forEach(gear => {
                            if (gear.match(/^[1-6]$/)) allGears.add(parseInt(gear));
                        });
                    });
                    
                    const sortedGears = Array.from(allGears).sort((a, b) => a - b);
                    
                    // Create traces for each driver
                    const traces = driverIds.map((driverId, index) => {
                        const driver = drivers[driverId];
                        const gearUsage = driver.session_data.gear_usage;
                        const totalShifts = Object.values(gearUsage).reduce((sum, count) => sum + count, 0);
                        
                        const gearPercentages = sortedGears.map(gear => {
                            const count = gearUsage[gear.toString()] || 0;
                            return totalShifts > 0 ? (count / totalShifts * 100) : 0;
                        });
                        
                        const colors = ['#667eea', '#764ba2', '#28a745', '#ffc107', '#dc3545', '#17a2b8'];
                        
                        return {
                            x: sortedGears.map(g => `Gear ${g}`),
                            y: gearPercentages,
                            type: 'bar',
                            name: driverId.split(' ')[0], // Shortened driver name
                            marker: { color: colors[index % colors.length] },
                            text: gearPercentages.map(p => `${p.toFixed(1)}%`),
                            textposition: 'auto'
                        };
                    });
                    
                    const layout = {
                        title: 'Gear Usage Comparison Between Drivers',
                        xaxis: { title: 'Gear' },
                        yaxis: { title: 'Usage Percentage (%)' },
                        barmode: 'group',
                        legend: { orientation: 'h', y: -0.2 }
                    };
                    
                    Plotly.newPlot('gearComparisonChart', traces, layout);
                    
                    // Add gear comparison insights
                    addGearComparisonInsights(drivers, sortedGears);
                }
                
                function addGearComparisonInsights(drivers, gears) {
                    const driverIds = Object.keys(drivers);
                    
                    if (driverIds.length < 2) return;
                    
                    let insights = [];
                    
                    // Analyze high gear usage differences
                    const highGearUsage = driverIds.map(id => {
                        const gearUsage = drivers[id].session_data.gear_usage;
                        const totalShifts = Object.values(gearUsage).reduce((sum, count) => sum + count, 0);
                        const highGearCount = (gearUsage['5'] || 0) + (gearUsage['6'] || 0);
                        return {
                            driver: id.split(' ')[0],
                            percentage: totalShifts > 0 ? (highGearCount / totalShifts * 100) : 0
                        };
                    });
                    
                    highGearUsage.sort((a, b) => b.percentage - a.percentage);
                    
                    if (highGearUsage.length >= 2) {
                        const best = highGearUsage[0];
                        const worst = highGearUsage[highGearUsage.length - 1];
                        const difference = best.percentage - worst.percentage;
                        
                        if (difference > 15) {
                            insights.push(`
                                <div class="alert alert-info alert-sm mb-2">
                                    <strong>High Gear Analysis:</strong> ${best.driver} uses high gears ${difference.toFixed(1)}% more than ${worst.driver}. 
                                    This suggests better corner exit speed and straight-line performance.
                                </div>
                            `);
                        }
                    }
                    
                    // Analyze gear range differences
                    const gearRanges = driverIds.map(id => {
                        const gearUsage = drivers[id].session_data.gear_usage;
                        const usedGears = Object.keys(gearUsage).filter(g => g.match(/^[1-6]$/) && gearUsage[g] > 0);
                        const gearNums = usedGears.map(g => parseInt(g));
                        return {
                            driver: id.split(' ')[0],
                            range: gearNums.length > 0 ? Math.max(...gearNums) - Math.min(...gearNums) + 1 : 0,
                            minGear: gearNums.length > 0 ? Math.min(...gearNums) : 0,
                            maxGear: gearNums.length > 0 ? Math.max(...gearNums) : 0
                        };
                    });
                    
                    const maxRange = Math.max(...gearRanges.map(r => r.range));
                    const minRange = Math.min(...gearRanges.map(r => r.range));
                    
                    if (maxRange - minRange >= 2) {
                        const bestRange = gearRanges.find(r => r.range === maxRange);
                        insights.push(`
                            <div class="alert alert-success alert-sm mb-2">
                                <strong>Gear Range:</strong> ${bestRange.driver} uses the widest gear range (${bestRange.range} gears), 
                                showing better track utilization and speed variation management.
                            </div>
                        `);
                    }
                    
                    // Display insights below the gear comparison chart
                    const insightsContainer = document.createElement('div');
                    insightsContainer.innerHTML = insights.join('');
                    
                    const chartContainer = document.getElementById('gearComparisonChart').parentNode;
                    const existingInsights = chartContainer.querySelector('.gear-comparison-insights');
                    if (existingInsights) {
                        existingInsights.remove();
                    }
                    
                    insightsContainer.className = 'gear-comparison-insights mt-3';
                    chartContainer.appendChild(insightsContainer);
                }
                
                function showSectorAnalysis(sectorAnalysis) {
                    if (!sectorAnalysis || Object.keys(sectorAnalysis).length === 0) {
                        document.getElementById('sectorAnalysis').innerHTML = '<p class="text-muted">No sector data available</p>';
                        return;
                    }
                    
                    // Create clear, coaching-focused sector analysis
                    let sectorHtml = `
                        <div class="alert alert-primary mb-3">
                            <h6 class="mb-2">Track Performance Report</h6>
                            <small>Analysis of your performance in each track section</small>
                        </div>
                    `;
                    
                    const sectorNames = {
                        'S1': 'Start/Finish Straight & Turn 1 Complex',
                        'S2': 'Middle Technical Section', 
                        'S3': 'Final Corners & Back Straight'
                    };
                    
                    ['S1', 'S2', 'S3'].forEach(sector => {
                        if (sectorAnalysis[sector]) {
                            const data = sectorAnalysis[sector];
                            const speedDiff = data.baseline_comparison.speed_vs_baseline;
                            const lateralGDiff = data.baseline_comparison.lateral_g_vs_baseline;
                            
                            // Determine performance status
                            let status, statusColor, statusIcon, timeGain;
                            
                            if (speedDiff > 3) {
                                status = 'STRONG SECTOR';
                                statusColor = 'success';
                                statusIcon = '[STRONG]';
                                timeGain = `+${(speedDiff * 0.1).toFixed(2)}s advantage`;
                            } else if (speedDiff > -3) {
                                status = 'COMPETITIVE';
                                statusColor = 'warning';
                                statusIcon = '[OK]';
                                timeGain = 'Matching field pace';
                            } else {
                                status = 'NEEDS WORK';
                                statusColor = 'danger';
                                statusIcon = '[FOCUS]';
                                timeGain = `${Math.abs(speedDiff * 0.1).toFixed(2)}s time loss`;
                            }
                            
                            // Generate specific coaching advice
                            let coachingAdvice = '';
                            
                            if (speedDiff < -5) {
                                coachingAdvice = `<strong>Priority Focus:</strong> You're losing significant time here. `;
                                if (lateralGDiff < -10) {
                                    coachingAdvice += `Push harder through corners - you have more grip available. `;
                                }
                                coachingAdvice += `Work on carrying more speed through this section.`;
                            } else if (speedDiff > 5) {
                                coachingAdvice = `<strong>Excellent!</strong> This is your strongest sector. Use this confidence to improve other areas.`;
                            } else {
                                if (lateralGDiff < -8) {
                                    coachingAdvice = `<strong>Opportunity:</strong> You can push the car harder through corners here.`;
                                } else if (data.baseline_comparison.throttle_vs_baseline < -10) {
                                    coachingAdvice = `<strong>Tip:</strong> Get on throttle earlier and more aggressively.`;
                                } else {
                                    coachingAdvice = `<strong>Good pace.</strong> Fine-tune your line and braking points for extra time.`;
                                }
                            }
                            
                            sectorHtml += `
                                <div class="card mb-2">
                                    <div class="card-body p-3">
                                        <div class="d-flex justify-content-between align-items-start mb-2">
                                            <div>
                                                <h6 class="mb-1">${statusIcon} ${sector}: ${sectorNames[sector]}</h6>
                                                <span class="badge bg-${statusColor}">${status}</span>
                                            </div>
                                            <div class="text-end">
                                                <small class="text-muted">${timeGain}</small>
                                            </div>
                                        </div>
                                        
                                        <div class="row mb-2">
                                            <div class="col-6">
                                                <small class="text-muted">Speed vs Field:</small><br>
                                                <strong class="${speedDiff > 0 ? 'text-success' : speedDiff < -3 ? 'text-danger' : 'text-warning'}">
                                                    ${speedDiff > 0 ? '+' : ''}${speedDiff.toFixed(1)}%
                                                </strong>
                                            </div>
                                            <div class="col-6">
                                                <small class="text-muted">Cornering:</small><br>
                                                <strong class="${lateralGDiff > 0 ? 'text-success' : lateralGDiff < -8 ? 'text-danger' : 'text-warning'}">
                                                    ${lateralGDiff > 0 ? '+' : ''}${lateralGDiff.toFixed(1)}% G-Force
                                                </strong>
                                            </div>
                                        </div>
                                        
                                        <div class="alert alert-light mb-0 p-2">
                                            <small>${coachingAdvice}</small>
                                        </div>
                                    </div>
                                </div>
                            `;
                        }
                    });
                    
                    // Add overall summary with actionable next steps
                    const sectors = Object.keys(sectorAnalysis);
                    if (sectors.length > 0) {
                        const worstSector = sectors.reduce((worst, sector) => 
                            sectorAnalysis[sector].baseline_comparison.speed_vs_baseline < 
                            sectorAnalysis[worst].baseline_comparison.speed_vs_baseline ? sector : worst);
                        
                        const bestSector = sectors.reduce((best, sector) => 
                            sectorAnalysis[sector].baseline_comparison.speed_vs_baseline > 
                            sectorAnalysis[best].baseline_comparison.speed_vs_baseline ? sector : best);
                        
                        const worstSpeedDiff = sectorAnalysis[worstSector].baseline_comparison.speed_vs_baseline;
                        const potentialGain = Math.abs(worstSpeedDiff * 0.1);
                        
                        sectorHtml += `
                            <div class="alert alert-info mt-3">
                                <h6>Next Session Focus</h6>
                                <p class="mb-1"><strong>Priority:</strong> Work on ${worstSector} (${sectorNames[worstSector]})</p>
                                <p class="mb-1"><strong>Potential Gain:</strong> Up to ${potentialGain.toFixed(2)} seconds per lap</p>
                                <p class="mb-0"><strong>Strength:</strong> Build on ${bestSector} performance</p>
                            </div>
                        `;
                    }
                    
                    document.getElementById('sectorAnalysis').innerHTML = sectorHtml;
                }
                
                function showGearAnalysis(gearUsage, insights) {
                    // Calculate total shifts and percentages
                    const totalShifts = Object.values(gearUsage).reduce((sum, count) => sum + count, 0);
                    const gearPercentages = {};
                    
                    Object.entries(gearUsage).forEach(([gear, count]) => {
                        gearPercentages[gear] = ((count / totalShifts) * 100).toFixed(1);
                    });
                    
                    // Display gear usage summary
                    const gearSummary = Object.entries(gearUsage)
                        .sort(([a], [b]) => parseInt(a) - parseInt(b))
                        .map(([gear, count]) => {
                            const percentage = gearPercentages[gear];
                            return `
                                <div class="d-flex justify-content-between align-items-center mb-1">
                                    <span><strong>Gear ${gear}:</strong></span>
                                    <span>${count} times (${percentage}%)</span>
                                </div>
                            `;
                        }).join('');
                    
                    document.getElementById('gearUsage').innerHTML = `
                        <div class="mb-2">
                            <small class="text-muted">Total gear changes: ${totalShifts}</small>
                        </div>
                        ${gearSummary}
                    `;
                    
                    // Create gear usage chart
                    const gears = Object.keys(gearUsage).sort((a, b) => parseInt(a) - parseInt(b));
                    const counts = gears.map(gear => gearUsage[gear]);
                    const percentages = gears.map(gear => parseFloat(gearPercentages[gear]));
                    
                    const trace = {
                        x: gears.map(g => `Gear ${g}`),
                        y: percentages,
                        type: 'bar',
                        marker: {
                            color: gears.map(g => {
                                const gearNum = parseInt(g);
                                if (gearNum <= 2) return '#dc3545'; // Low gears - red
                                if (gearNum <= 4) return '#ffc107'; // Mid gears - yellow
                                return '#28a745'; // High gears - green
                            })
                        },
                        text: percentages.map(p => `${p}%`),
                        textposition: 'auto'
                    };
                    
                    const layout = {
                        title: 'Gear Usage Distribution',
                        xaxis: { title: 'Gear' },
                        yaxis: { title: 'Usage (%)' },
                        margin: { t: 40, b: 40, l: 40, r: 40 }
                    };
                    
                    Plotly.newPlot('gearChart', [trace], layout, {displayModeBar: false});
                    
                    // Show gear-specific insights
                    const gearInsights = insights.filter(insight => insight.category === 'Gear Usage');
                    const gearInsightsHtml = gearInsights.map(insight => `
                        <div class="alert alert-sm insight-${insight.type} mb-1 p-2">
                            <small><strong>${insight.category}:</strong> ${insight.message}</small>
                        </div>
                    `).join('');
                    
                    // Add gear usage explanations
                    const explanationHtml = `
                        <div class="mt-2">
                            <small class="text-muted">
                                <strong>Gear Usage Guide:</strong><br>
                                - <span style="color: #dc3545;">Low gears (1-2):</span> Corner entry/exit<br>
                                - <span style="color: #ffc107;">Mid gears (3-4):</span> Corner transitions<br>
                                - <span style="color: #28a745;">High gears (5-6):</span> Straights/fast corners
                            </small>
                        </div>
                    `;
                    
                    document.getElementById('gearInsights').innerHTML = gearInsightsHtml + explanationHtml;
                }
            </script>
        </body>
        </html>
        """
        
        return create_response(200, dashboard_html, 'text/html')
    
    else:
        return create_response(404, {"error": "Not Found"})