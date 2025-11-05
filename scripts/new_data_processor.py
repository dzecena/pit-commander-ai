"""
New Data Integration Processor

Handles new telemetry data integration with baseline comparison
and automated performance analysis updates.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Any
import boto3

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewDataProcessor:
    """
    Process new telemetry data and compare with existing baselines
    """
    
    def __init__(self):
        self.baseline_dir = Path("data/baselines")
        self.baseline_dir.mkdir(exist_ok=True)
        
        self.s3_client = boto3.client('s3')
        self.bucket_name = "gr-cup-data-dev-us-east-1-v2"
        
    def validate_data_format(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate that new data matches required format
        """
        required_columns = [
            'vehicle_id', 'timestamp', 'meta_time', 'lap', 'Speed',
            'pbrake_f', 'ath', 'Steering_Angle', 'accx_can', 'accy_can',
            'nmotor', 'Gear', 'track_name', 'track_id'
        ]
        
        validation_result = {
            'valid': True,
            'missing_columns': [],
            'data_quality': {},
            'recommendations': []
        }
        
        # Check required columns
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            validation_result['valid'] = False
            validation_result['missing_columns'] = missing_cols
        
        # Check data quality
        if 'vehicle_id' in df.columns:
            # Validate vehicle ID format
            invalid_ids = df[~df['vehicle_id'].str.match(r'GR86-\d{3}-\d{3}', na=False)]
            if len(invalid_ids) > 0:
                validation_result['data_quality']['invalid_vehicle_ids'] = len(invalid_ids)
                validation_result['recommendations'].append(
                    f"Fix {len(invalid_ids)} invalid vehicle IDs. Format should be GR86-XXX-XXX"
                )
        
        # Check for lap errors
        if 'lap' in df.columns:
            lap_errors = (df['lap'] == 32768).sum()
            if lap_errors > 0:
                validation_result['data_quality']['lap_errors'] = lap_errors
                validation_result['recommendations'].append(
                    f"Found {lap_errors} lap count errors (32768). Will be auto-corrected."
                )
        
        # Check data completeness
        total_records = len(df)
        null_counts = df.isnull().sum()
        critical_nulls = null_counts[['Speed', 'lap', 'timestamp']].sum()
        
        if critical_nulls > total_records * 0.1:  # More than 10% missing critical data
            validation_result['valid'] = False
            validation_result['recommendations'].append(
                f"Too much missing critical data: {critical_nulls}/{total_records} records"
            )
        
        validation_result['data_quality']['total_records'] = total_records
        validation_result['data_quality']['null_percentages'] = (null_counts / total_records * 100).to_dict()
        
        return validation_result
    
    def load_or_create_baseline(self, track_id: str) -> Dict[str, Any]:
        """
        Load existing baseline or create new one
        """
        baseline_file = self.baseline_dir / f"{track_id}_baseline_metrics.json"
        
        if baseline_file.exists():
            with open(baseline_file, 'r') as f:
                baseline = json.load(f)
            logger.info(f"Loaded existing baseline for {track_id}")
        else:
            # Create new baseline structure
            baseline = {
                'track_id': track_id,
                'created_date': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'total_sessions': 0,
                'total_drivers': 0,
                'sector_benchmarks': {
                    'S1': {'avg_speed': 0, 'avg_lateral_g': 0, 'sample_count': 0},
                    'S2': {'avg_speed': 0, 'avg_lateral_g': 0, 'sample_count': 0},
                    'S3': {'avg_speed': 0, 'avg_lateral_g': 0, 'sample_count': 0}
                },
                'overall_benchmarks': {
                    'field_avg_speed': 0,
                    'field_max_speed': 0,
                    'field_avg_braking': 0,
                    'field_avg_lateral_g': 0
                },
                'driver_records': {},
                'lap_time_percentiles': {
                    'p10': 0, 'p25': 0, 'p50': 0, 'p75': 0, 'p90': 0
                }
            }
            logger.info(f"Created new baseline for {track_id}")
        
        return baseline
    
    def update_baseline_with_new_data(self, baseline: Dict[str, Any], new_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Update baseline metrics with new session data
        """
        track_id = baseline['track_id']
        
        # Update session count
        baseline['total_sessions'] += 1
        baseline['last_updated'] = datetime.now().isoformat()
        
        # Update driver count
        new_drivers = new_df['vehicle_id'].unique()
        existing_drivers = set(baseline['driver_records'].keys())
        all_drivers = existing_drivers.union(set(new_drivers))
        baseline['total_drivers'] = len(all_drivers)
        
        # Update overall benchmarks using weighted average
        current_weight = baseline['total_sessions'] - 1
        new_weight = 1
        total_weight = current_weight + new_weight
        
        if total_weight > 0:
            # Speed benchmarks
            new_avg_speed = new_df['Speed'].mean()
            new_max_speed = new_df['Speed'].max()
            
            baseline['overall_benchmarks']['field_avg_speed'] = (
                baseline['overall_benchmarks']['field_avg_speed'] * current_weight + 
                new_avg_speed * new_weight
            ) / total_weight
            
            baseline['overall_benchmarks']['field_max_speed'] = max(
                baseline['overall_benchmarks']['field_max_speed'],
                new_max_speed
            )
            
            # Braking benchmarks
            new_avg_braking = new_df['pbrake_f'].mean()
            baseline['overall_benchmarks']['field_avg_braking'] = (
                baseline['overall_benchmarks']['field_avg_braking'] * current_weight + 
                new_avg_braking * new_weight
            ) / total_weight
            
            # Lateral G benchmarks
            new_avg_lateral_g = abs(new_df['accy_can']).mean()
            baseline['overall_benchmarks']['field_avg_lateral_g'] = (
                baseline['overall_benchmarks']['field_avg_lateral_g'] * current_weight + 
                new_avg_lateral_g * new_weight
            ) / total_weight
        
        # Update sector benchmarks (simplified - in practice you'd use GPS/timing data)
        for sector in ['S1', 'S2', 'S3']:
            # Estimate sector data (in real implementation, use timing beacons)
            sector_data = new_df.sample(frac=0.33)  # Simplified sector estimation
            
            if len(sector_data) > 0:
                sector_avg_speed = sector_data['Speed'].mean()
                sector_avg_lateral_g = abs(sector_data['accy_can']).mean()
                
                current_count = baseline['sector_benchmarks'][sector]['sample_count']
                new_count = len(sector_data)
                total_count = current_count + new_count
                
                if total_count > 0:
                    baseline['sector_benchmarks'][sector]['avg_speed'] = (
                        baseline['sector_benchmarks'][sector]['avg_speed'] * current_count + 
                        sector_avg_speed * new_count
                    ) / total_count
                    
                    baseline['sector_benchmarks'][sector]['avg_lateral_g'] = (
                        baseline['sector_benchmarks'][sector]['avg_lateral_g'] * current_count + 
                        sector_avg_lateral_g * new_count
                    ) / total_count
                    
                    baseline['sector_benchmarks'][sector]['sample_count'] = total_count
        
        # Update driver records
        for driver_id in new_drivers:
            driver_data = new_df[new_df['vehicle_id'] == driver_id]
            
            driver_metrics = {
                'last_session': datetime.now().isoformat(),
                'total_sessions': baseline['driver_records'].get(driver_id, {}).get('total_sessions', 0) + 1,
                'best_speed': max(
                    baseline['driver_records'].get(driver_id, {}).get('best_speed', 0),
                    driver_data['Speed'].max()
                ),
                'avg_speed': driver_data['Speed'].mean(),
                'total_laps': driver_data['lap'].nunique(),
                'chassis': driver_data['vehicle_id'].iloc[0].split('-')[1] if len(driver_data) > 0 else 'unknown',
                'car_number': driver_data['vehicle_id'].iloc[0].split('-')[2] if len(driver_data) > 0 else 'unknown'
            }
            
            baseline['driver_records'][driver_id] = driver_metrics
        
        return baseline
    
    def generate_comparison_report(self, baseline: Dict[str, Any], new_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate detailed comparison report for new data vs baseline
        """
        report = {
            'session_date': datetime.now().isoformat(),
            'track_id': baseline['track_id'],
            'new_data_summary': {
                'total_records': len(new_df),
                'unique_drivers': new_df['vehicle_id'].nunique(),
                'total_laps': new_df['lap'].nunique(),
                'session_duration_minutes': (new_df['timestamp'].max() - new_df['timestamp'].min()) / (1000 * 60)
            },
            'performance_vs_baseline': {},
            'driver_analysis': {},
            'recommendations': []
        }
        
        # Overall performance vs baseline
        new_avg_speed = new_df['Speed'].mean()
        baseline_avg_speed = baseline['overall_benchmarks']['field_avg_speed']
        
        if baseline_avg_speed > 0:
            speed_improvement = ((new_avg_speed - baseline_avg_speed) / baseline_avg_speed) * 100
            
            report['performance_vs_baseline'] = {
                'speed_vs_baseline': round(speed_improvement, 2),
                'new_session_avg_speed': round(new_avg_speed, 1),
                'baseline_avg_speed': round(baseline_avg_speed, 1),
                'performance_rating': 'Above Baseline' if speed_improvement > 2 else 
                                   'At Baseline' if speed_improvement > -2 else 'Below Baseline'
            }
        
        # Individual driver analysis
        for driver_id in new_df['vehicle_id'].unique():
            driver_data = new_df[new_df['vehicle_id'] == driver_id]
            driver_baseline = baseline['driver_records'].get(driver_id, {})
            
            driver_analysis = {
                'is_new_driver': driver_id not in baseline['driver_records'],
                'session_performance': {
                    'max_speed': round(driver_data['Speed'].max(), 1),
                    'avg_speed': round(driver_data['Speed'].mean(), 1),
                    'laps_completed': driver_data['lap'].nunique(),
                    'consistency': round(100 - (driver_data['Speed'].std() / driver_data['Speed'].mean() * 100), 1)
                }
            }
            
            if not driver_analysis['is_new_driver']:
                # Compare with driver's historical performance
                historical_best = driver_baseline.get('best_speed', 0)
                current_best = driver_data['Speed'].max()
                
                if historical_best > 0:
                    improvement = ((current_best - historical_best) / historical_best) * 100
                    driver_analysis['vs_personal_best'] = {
                        'speed_improvement': round(improvement, 2),
                        'new_personal_best': current_best > historical_best
                    }
            
            report['driver_analysis'][driver_id] = driver_analysis
        
        # Generate recommendations
        if report['performance_vs_baseline'].get('speed_vs_baseline', 0) < -5:
            report['recommendations'].append("Session performance below baseline - focus on setup and driving technique")
        
        new_drivers = [d for d, a in report['driver_analysis'].items() if a['is_new_driver']]
        if new_drivers:
            report['recommendations'].append(f"New drivers detected: {', '.join(new_drivers)} - provide baseline coaching")
        
        return report
    
    def process_new_data_file(self, file_path: str) -> Dict[str, Any]:
        """
        Main processing function for new data files
        """
        logger.info(f"Processing new data file: {file_path}")
        
        try:
            # Load new data
            new_df = pd.read_csv(file_path)
            track_id = new_df['track_id'].iloc[0] if 'track_id' in new_df.columns else 'UNKNOWN'
            
            # Validate data format
            validation = self.validate_data_format(new_df)
            if not validation['valid']:
                logger.error(f"Data validation failed: {validation}")
                return {'success': False, 'error': 'Data validation failed', 'details': validation}
            
            # Clean the new data (same process as baseline)
            from src.data_processing.data_cleaner import GRCupDataCleaner
            cleaner = GRCupDataCleaner(track_id)
            cleaned_df = cleaner.clean_telemetry(file_path)
            
            # Load/create baseline
            baseline = self.load_or_create_baseline(track_id)
            
            # Generate comparison report BEFORE updating baseline
            comparison_report = self.generate_comparison_report(baseline, cleaned_df)
            
            # Update baseline with new data
            updated_baseline = self.update_baseline_with_new_data(baseline, cleaned_df)
            
            # Save updated baseline
            baseline_file = self.baseline_dir / f"{track_id}_baseline_metrics.json"
            with open(baseline_file, 'w') as f:
                json.dump(updated_baseline, f, indent=2)
            
            # Upload to S3
            s3_key = f"processed-telemetry/{track_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_telemetry_clean.csv"
            cleaned_df.to_csv(f"temp_{track_id}.csv", index=False)
            
            self.s3_client.upload_file(
                f"temp_{track_id}.csv",
                self.bucket_name,
                s3_key
            )
            
            # Clean up temp file
            Path(f"temp_{track_id}.csv").unlink()
            
            logger.info(f"Successfully processed new data for {track_id}")
            
            return {
                'success': True,
                'track_id': track_id,
                'validation': validation,
                'comparison_report': comparison_report,
                'baseline_updated': True,
                's3_location': f"s3://{self.bucket_name}/{s3_key}"
            }
            
        except Exception as e:
            logger.error(f"Error processing new data: {e}")
            return {'success': False, 'error': str(e)}

def main():
    """
    Example usage of new data processor
    """
    processor = NewDataProcessor()
    
    # Process a new data file
    result = processor.process_new_data_file("path/to/new/BMP_20251104_PRACTICE.csv")
    
    if result['success']:
        print("✅ New data processed successfully!")
        print(f"Track: {result['track_id']}")
        print(f"Comparison Report: {json.dumps(result['comparison_report'], indent=2)}")
    else:
        print(f"❌ Processing failed: {result['error']}")

if __name__ == "__main__":
    main()