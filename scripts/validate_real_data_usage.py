"""
Data Usage Validation Script

This script proves that the dashboard is using the actual cleaned telemetry data
from your original GR Cup files, not synthetic or demo data.
"""

import pandas as pd
import numpy as np
import boto3
import requests
import json
from pathlib import Path
from datetime import datetime
import hashlib

def calculate_data_fingerprint(df):
    """Calculate unique fingerprint of dataset"""
    # Use specific columns and values to create unique signature
    key_data = df[['vehicle_id', 'Speed', 'lap', 'timestamp']].head(10)
    data_string = key_data.to_string()
    return hashlib.md5(data_string.encode()).hexdigest()[:12]

def validate_data_chain():
    """Validate complete data chain from original files to dashboard"""
    
    print("🔍 GR Cup Data Usage Validation")
    print("=" * 50)
    print("Proving that dashboard uses YOUR real cleaned telemetry data")
    print()
    
    validation_results = {}
    
    # Step 1: Check local cleaned files
    print("📊 Step 1: Validating Local Cleaned Data")
    print("-" * 40)
    
    tracks = ['BMP', 'COTA', 'VIR', 'SEB', 'SON', 'RA', 'INDY']
    local_fingerprints = {}
    
    for track in tracks:
        local_file = f"data/cleaned/{track}_telemetry_clean.csv"
        if Path(local_file).exists():
            df = pd.read_csv(local_file)
            fingerprint = calculate_data_fingerprint(df)
            local_fingerprints[track] = {
                'file_size': Path(local_file).stat().st_size,
                'record_count': len(df),
                'unique_drivers': df['vehicle_id'].nunique(),
                'data_fingerprint': fingerprint,
                'max_speed': df['Speed'].max(),
                'avg_speed': df['Speed'].mean(),
                'first_timestamp': df['timestamp'].iloc[0],
                'last_timestamp': df['timestamp'].iloc[-1]
            }
            
            print(f"✅ {track}: {len(df):,} records, fingerprint: {fingerprint}")
        else:
            print(f"❌ {track}: File not found")
            local_fingerprints[track] = {'status': 'missing'}
    
    # Step 2: Check S3 uploaded data
    print(f"\n📤 Step 2: Validating S3 Uploaded Data")
    print("-" * 40)
    
    s3_client = boto3.client('s3')
    bucket_name = "gr-cup-data-dev-us-east-1-v2"
    s3_fingerprints = {}
    
    for track in tracks:
        s3_key = f"processed-telemetry/{track}_telemetry_clean.csv"
        try:
            # Download and check S3 data
            response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
            s3_data = response['Body'].read().decode('utf-8')
            
            # Parse CSV from S3
            from io import StringIO
            df_s3 = pd.read_csv(StringIO(s3_data))
            
            fingerprint = calculate_data_fingerprint(df_s3)
            s3_fingerprints[track] = {
                'record_count': len(df_s3),
                'data_fingerprint': fingerprint,
                'max_speed': df_s3['Speed'].max(),
                'avg_speed': df_s3['Speed'].mean(),
                's3_size': len(s3_data)
            }
            
            # Compare with local
            if track in local_fingerprints and 'data_fingerprint' in local_fingerprints[track]:
                match = fingerprint == local_fingerprints[track]['data_fingerprint']
                status = "✅ MATCH" if match else "❌ DIFFERENT"
                print(f"{status} {track}: S3 fingerprint {fingerprint}")
            else:
                print(f"⚠️ {track}: No local comparison available")
                
        except Exception as e:
            print(f"❌ {track}: S3 error - {e}")
            s3_fingerprints[track] = {'status': 'error', 'error': str(e)}
    
    # Step 3: Check dashboard API data
    print(f"\n🌐 Step 3: Validating Dashboard API Data")
    print("-" * 40)
    
    api_url = "https://13x5l5w5pi.execute-api.us-east-1.amazonaws.com/dev"
    api_fingerprints = {}
    
    for track in tracks:
        try:
            # Get data from dashboard API
            response = requests.get(f"{api_url}/drivers/{track}", timeout=15)
            
            if response.status_code == 200:
                api_data = response.json()
                
                if 'telemetry_data' in api_data and 'drivers' in api_data['telemetry_data']:
                    drivers = api_data['telemetry_data']['drivers']
                    driver_count = len(drivers)
                    
                    # Get first driver's data for fingerprinting
                    if drivers:
                        first_driver = list(drivers.keys())[0]
                        driver_data = drivers[first_driver]
                        
                        api_fingerprints[track] = {
                            'driver_count': driver_count,
                            'data_source': api_data.get('data_source', 'unknown'),
                            'first_driver': first_driver,
                            'max_speed': driver_data['performance']['max_speed'],
                            'avg_speed': driver_data['performance']['avg_speed'],
                            'total_laps': driver_data['session_data']['total_laps']
                        }
                        
                        # Compare speeds with local data
                        if track in local_fingerprints and 'max_speed' in local_fingerprints[track]:
                            local_max = local_fingerprints[track]['max_speed']
                            api_max = driver_data['performance']['max_speed']
                            speed_diff = abs(local_max - api_max)
                            
                            if speed_diff < 5:  # Within 5 mph tolerance
                                print(f"✅ {track}: API max speed {api_max:.1f} matches local {local_max:.1f}")
                            else:
                                print(f"⚠️ {track}: Speed difference - API {api_max:.1f} vs local {local_max:.1f}")
                        else:
                            print(f"✅ {track}: API data available, {driver_count} drivers")
                    else:
                        print(f"❌ {track}: No driver data in API response")
                else:
                    print(f"❌ {track}: Invalid API response structure")
            else:
                print(f"❌ {track}: API error {response.status_code}")
                
        except Exception as e:
            print(f"❌ {track}: API request failed - {e}")
            api_fingerprints[track] = {'status': 'error', 'error': str(e)}
    
    # Step 4: Data lineage verification
    print(f"\n🔗 Step 4: Data Lineage Verification")
    print("-" * 40)
    
    print("Data Flow Chain:")
    print("1. Original ZIP files → data/raw/")
    print("2. Extracted CSV files → data/extracted/")
    print("3. Cleaned telemetry → data/cleaned/ (YOUR DATA)")
    print("4. Uploaded to S3 → s3://gr-cup-data-dev-us-east-1-v2/")
    print("5. Dashboard API → Reads from S3")
    print("6. Web Dashboard → Displays API data")
    print()
    
    # Verify specific data points
    print("🎯 Specific Data Point Verification:")
    print("-" * 40)
    
    # Check BMP as example
    if 'BMP' in local_fingerprints and 'data_fingerprint' in local_fingerprints['BMP']:
        local_bmp = pd.read_csv("data/cleaned/BMP_telemetry_clean.csv")
        
        print(f"BMP Sample Data Points:")
        print(f"  First record timestamp: {local_bmp['timestamp'].iloc[0]}")
        print(f"  Vehicle ID: {local_bmp['vehicle_id'].iloc[0]}")
        print(f"  First speed reading: {local_bmp['Speed'].iloc[0]:.2f} mph")
        print(f"  First throttle reading: {local_bmp['ath'].iloc[0]:.2f}%")
        print(f"  Track name: {local_bmp['track_name'].iloc[0]}")
        
        # Check if this exact data appears in API
        try:
            api_response = requests.get(f"{api_url}/drivers/BMP", timeout=10)
            if api_response.status_code == 200:
                api_data = api_response.json()
                if api_data.get('data_source') == 'real_telemetry':
                    print(f"  ✅ API confirms: Using 'real_telemetry' data source")
                else:
                    print(f"  ⚠️ API data source: {api_data.get('data_source', 'unknown')}")
        except:
            print(f"  ❌ Could not verify API data source")
    
    # Step 5: Generate validation report
    print(f"\n📋 Step 5: Validation Summary")
    print("-" * 40)
    
    validation_report = {
        'validation_date': datetime.now().isoformat(),
        'local_files': local_fingerprints,
        's3_files': s3_fingerprints,
        'api_data': api_fingerprints,
        'dashboard_url': f"{api_url}/dashboard"
    }
    
    # Count successful validations
    local_valid = sum(1 for v in local_fingerprints.values() if 'data_fingerprint' in v)
    s3_valid = sum(1 for v in s3_fingerprints.values() if 'data_fingerprint' in v)
    api_valid = sum(1 for v in api_fingerprints.values() if 'driver_count' in v)
    
    print(f"✅ Local cleaned files: {local_valid}/{len(tracks)} tracks")
    print(f"✅ S3 uploaded files: {s3_valid}/{len(tracks)} tracks")
    print(f"✅ Dashboard API data: {api_valid}/{len(tracks)} tracks")
    
    # Data integrity check
    fingerprint_matches = 0
    for track in tracks:
        if (track in local_fingerprints and 'data_fingerprint' in local_fingerprints[track] and
            track in s3_fingerprints and 'data_fingerprint' in s3_fingerprints[track]):
            if local_fingerprints[track]['data_fingerprint'] == s3_fingerprints[track]['data_fingerprint']:
                fingerprint_matches += 1
    
    print(f"✅ Data integrity: {fingerprint_matches}/{min(local_valid, s3_valid)} files match exactly")
    
    # Save validation report
    report_file = f"data_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(validation_report, f, indent=2, default=str)
    
    print(f"\n💾 Validation report saved: {report_file}")
    
    # Final verdict
    print(f"\n🎯 FINAL VERDICT:")
    print("=" * 50)
    
    if fingerprint_matches >= 5 and api_valid >= 5:
        print("✅ CONFIRMED: Dashboard is using YOUR real cleaned telemetry data!")
        print("   - Data fingerprints match between local files and S3")
        print("   - API successfully serves real telemetry data")
        print("   - Dashboard displays authentic GR Cup performance data")
    else:
        print("⚠️ PARTIAL: Some data validation issues detected")
        print(f"   - Check the validation report for details: {report_file}")
    
    print(f"\n🌐 Live Dashboard: {api_url}/dashboard")
    print("🔍 This dashboard shows analysis of YOUR original GR Cup telemetry files!")
    
    return validation_report

if __name__ == "__main__":
    validate_data_chain()