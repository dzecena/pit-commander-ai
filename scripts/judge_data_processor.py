"""
Judge Data Processor - Handle new pilot/car data without retraining

Author: GR Cup Analytics Team
Date: 2025-10-31

This script processes any new GR Cup data for immediate predictions:
- New drivers on existing tracks
- New cars with different setups
- New sessions with unknown participants
- Partial or incomplete data

No model retraining required!
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import sys
import argparse
import zipfile
import shutil
from datetime import datetime
import json

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from data_processing.data_cleaner import GRCupDataCleaner
from data_processing.sector_parser import SectorAnalyzer
from models.tire_degradation import TireDegradationModel
from models.pit_strategy import PitStrategyOptimizer
from utils.config import TRACKS, setup_logging

setup_logging()
logger = logging.getLogger(__name__)

class JudgeDataProcessor:
    """
    Process new judge data for immediate predictions
    """
    
    def __init__(self):
        self.model = TireDegradationModel()
        self.pit_optimizer = None
        self.processing_results = {
            'status': 'initialized',
            'files_processed': 0,
            'predictions_generated': 0,
            'confidence_level': 0.0,
            'warnings': [],
            'errors': []
        }
    
    def load_existing_model(self) -> bool:
        """
        Load the pre-trained model
        """
        logger.info("🤖 Loading existing trained model...")
        
        try:
            success = self.model.load_model()
            if success:
                self.pit_optimizer = PitStrategyOptimizer(self.model)
                logger.info("✅ Model loaded successfully")
                return True
            else:
                logger.error("❌ Failed to load model")
                return False
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            return False
    
    def detect_data_format(self, input_path: Path) -> dict:
        """
        Detect what type of data we're dealing with
        """
        logger.info(f"🔍 Detecting data format: {input_path.name}")
        
        detection_result = {
            'format': 'unknown',
            'track': 'unknown',
            'files': [],
            'confidence': 0.0
        }
        
        if input_path.is_file():
            if input_path.suffix.lower() == '.zip':
                detection_result['format'] = 'zip'
                detection_result['files'] = [input_path]
            elif input_path.suffix.lower() == '.csv':
                detection_result['format'] = 'csv'
                detection_result['files'] = [input_path]
            elif input_path.suffix.lower() == '.pdf':
                detection_result['format'] = 'pdf'
                detection_result['files'] = [input_path]
        
        elif input_path.is_dir():
            detection_result['format'] = 'directory'
            detection_result['files'] = list(input_path.glob("*"))
        
        # Try to identify track from filename/path
        path_str = str(input_path).lower()
        
        track_indicators = {
            'barber': 'BMP',
            'cota': 'COTA',
            'circuit': 'COTA',
            'americas': 'COTA',
            'indianapolis': 'INDY',
            'indy': 'INDY',
            'road-america': 'RA',
            'road america': 'RA',
            'sebring': 'SEB',
            'sonoma': 'SON',
            'vir': 'VIR',
            'virginia': 'VIR'
        }
        
        for indicator, track_abbrev in track_indicators.items():
            if indicator in path_str:
                detection_result['track'] = track_abbrev
                detection_result['confidence'] = 0.8
                break
        
        logger.info(f"  Format: {detection_result['format']}")
        logger.info(f"  Track: {detection_result['track']}")
        logger.info(f"  Files: {len(detection_result['files'])}")
        
        return detection_result
    
    def extract_data(self, input_path: Path, detection_result: dict) -> Path:
        """
        Extract data to a working directory
        """
        logger.info("📦 Extracting data...")
        
        # Create working directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        work_dir = Path(f"data/judge_sessions/session_{timestamp}")
        work_dir.mkdir(parents=True, exist_ok=True)
        
        if detection_result['format'] == 'zip':
            # Extract ZIP file
            with zipfile.ZipFile(input_path, 'r') as zip_ref:
                zip_ref.extractall(work_dir)
            logger.info(f"  ✅ Extracted ZIP to {work_dir}")
        
        elif detection_result['format'] == 'csv':
            # Copy CSV file
            shutil.copy2(input_path, work_dir / input_path.name)
            logger.info(f"  ✅ Copied CSV to {work_dir}")
        
        elif detection_result['format'] == 'directory':
            # Copy directory contents
            for file in detection_result['files']:
                if file.is_file():
                    shutil.copy2(file, work_dir / file.name)
            logger.info(f"  ✅ Copied directory contents to {work_dir}")
        
        return work_dir
    
    def identify_data_files(self, work_dir: Path) -> dict:
        """
        Identify telemetry, sector, and lap time files
        """
        logger.info("🔍 Identifying data files...")
        
        files = {
            'telemetry': [],
            'sectors': [],
            'lap_times': [],
            'results': [],
            'unknown': []
        }
        
        for file_path in work_dir.glob("*.csv"):
            filename_lower = file_path.name.lower()
            
            # Try to read first few rows to understand content
            try:
                df_sample = pd.read_csv(file_path, nrows=5)
                columns_lower = [str(col).lower() for col in df_sample.columns]
                
                # Classify based on columns
                if any(col in columns_lower for col in ['speed', 'rpm', 'throttle', 'brake', 'steering']):
                    files['telemetry'].append(file_path)
                    logger.info(f"  📊 Telemetry: {file_path.name}")
                
                elif any(col in columns_lower for col in ['im1a', 'im1', 'im2a', 'im2', 'im3a', 'fl']):
                    files['sectors'].append(file_path)
                    logger.info(f"  🎯 Sectors: {file_path.name}")
                
                elif any(col in columns_lower for col in ['lap_time', 'lap time', 'sector']):
                    files['lap_times'].append(file_path)
                    logger.info(f"  ⏱️  Lap Times: {file_path.name}")
                
                elif any(col in columns_lower for col in ['position', 'result', 'driver']):
                    files['results'].append(file_path)
                    logger.info(f"  🏁 Results: {file_path.name}")
                
                else:
                    files['unknown'].append(file_path)
                    logger.info(f"  ❓ Unknown: {file_path.name}")
            
            except Exception as e:
                logger.warning(f"  ⚠️  Could not read {file_path.name}: {e}")
                files['unknown'].append(file_path)
        
        return files
    
    def process_telemetry_data(self, telemetry_files: list, track_abbrev: str) -> pd.DataFrame:
        """
        Process telemetry data for new pilots/cars
        """
        logger.info("🏎️  Processing telemetry data...")
        
        if not telemetry_files:
            logger.warning("No telemetry files found")
            return pd.DataFrame()
        
        # Use the first telemetry file
        telemetry_file = telemetry_files[0]
        
        # Clean the data using existing pipeline
        cleaner = GRCupDataCleaner(f"JUDGE_{track_abbrev}")
        cleaned_df = cleaner.clean_telemetry(str(telemetry_file))
        
        logger.info(f"  ✅ Processed {len(cleaned_df)} telemetry records")
        
        # Analyze new drivers/cars
        if 'vehicle_id' in cleaned_df.columns:
            unique_vehicles = cleaned_df['vehicle_id'].unique()
            logger.info(f"  🚗 Found {len(unique_vehicles)} unique vehicles:")
            for vehicle in unique_vehicles[:5]:  # Show first 5
                logger.info(f"    - {vehicle}")
        
        return cleaned_df
    
    def generate_predictions(self, telemetry_df: pd.DataFrame, track_abbrev: str) -> dict:
        """
        Generate predictions for new data
        """
        logger.info("🔮 Generating predictions...")
        
        if telemetry_df.empty:
            logger.warning("No telemetry data available for predictions")
            return {}
        
        predictions = {
            'track': track_abbrev,
            'vehicles': {},
            'summary': {},
            'confidence': 0.0
        }
        
        try:
            # Prepare features for prediction
            features_df = self.model.prepare_features(telemetry_df)
            
            if features_df.empty:
                logger.warning("Could not prepare features for prediction")
                return predictions
            
            # Generate predictions for each vehicle
            for vehicle_id in telemetry_df['vehicle_id'].unique():
                if pd.isna(vehicle_id):
                    continue
                
                vehicle_data = features_df[features_df['vehicle_id'] == vehicle_id]
                
                if len(vehicle_data) == 0:
                    continue
                
                # Get latest data point for this vehicle
                latest_data = vehicle_data.iloc[-1]
                
                # Prepare feature dict
                feature_dict = {}
                for feature_name in self.model.feature_names:
                    if feature_name in latest_data:
                        feature_dict[feature_name] = latest_data[feature_name]
                    else:
                        # Use reasonable defaults
                        defaults = {
                            'tire_age': 10,
                            'driver_avg_pace': TRACKS.get(track_abbrev, {}).get('typical_lap_time', 120),
                            'track_avg_speed': 150.0,
                            'track_degradation_rate': 0.5,
                            'race_progress': 0.5,
                            'recent_pace_3lap': TRACKS.get(track_abbrev, {}).get('typical_lap_time', 120),
                            'session_best': TRACKS.get(track_abbrev, {}).get('typical_lap_time', 120) * 0.95,
                            'track_type_encoded': 1
                        }
                        feature_dict[feature_name] = defaults.get(feature_name, 0.0)
                
                # Make prediction
                prediction = self.model.predict_lap_time(feature_dict)
                
                predictions['vehicles'][str(vehicle_id)] = {
                    'predicted_lap_time': prediction['predicted_time'],
                    'confidence': prediction['confidence'],
                    'uncertainty': prediction['uncertainty'],
                    'tire_age': feature_dict.get('tire_age', 0),
                    'current_pace': latest_data.get('lap_time', 0)
                }
                
                logger.info(f"  🏎️  {vehicle_id}: {prediction['predicted_time']:.2f}s (confidence: {prediction['confidence']:.1%})")
            
            # Calculate overall confidence
            if predictions['vehicles']:
                avg_confidence = np.mean([v['confidence'] for v in predictions['vehicles'].values()])
                predictions['confidence'] = avg_confidence
                predictions['summary'] = {
                    'vehicles_analyzed': len(predictions['vehicles']),
                    'avg_predicted_time': np.mean([v['predicted_lap_time'] for v in predictions['vehicles'].values()]),
                    'avg_confidence': avg_confidence
                }
            
            self.processing_results['predictions_generated'] = len(predictions['vehicles'])
            self.processing_results['confidence_level'] = predictions['confidence']
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            self.processing_results['errors'].append(f"Prediction error: {e}")
        
        return predictions
    
    def generate_pit_strategy(self, predictions: dict, track_abbrev: str) -> dict:
        """
        Generate pit strategy recommendations
        """
        logger.info("🏁 Generating pit strategy...")
        
        if not predictions.get('vehicles'):
            return {}
        
        pit_strategies = {}
        
        try:
            for vehicle_id, vehicle_pred in predictions['vehicles'].items():
                # Simulate current race state
                current_state = {
                    'current_lap': 15,  # Mid-race scenario
                    'track_id': track_abbrev,
                    'position': 3,  # Assume mid-pack
                    'gap_ahead': 2.5,
                    'gap_behind': 4.0,
                    'tire_age': vehicle_pred.get('tire_age', 15),
                    'max_laps': 30,
                    'track_features': {
                        'tire_age': vehicle_pred.get('tire_age', 15),
                        'driver_avg_pace': vehicle_pred.get('current_pace', 120),
                        'track_avg_speed': 150.0,
                        'track_degradation_rate': 0.5,
                        'race_progress': 0.5,
                        'recent_pace_3lap': vehicle_pred.get('predicted_lap_time', 120),
                        'session_best': TRACKS.get(track_abbrev, {}).get('typical_lap_time', 120) * 0.95,
                        'track_type_encoded': 1
                    }
                }
                
                strategy = self.pit_optimizer.get_recommendation(current_state)
                pit_strategies[vehicle_id] = strategy
                
                logger.info(f"  🏎️  {vehicle_id}: {strategy['action']} - {strategy['reasoning']}")
        
        except Exception as e:
            logger.error(f"Error generating pit strategy: {e}")
            self.processing_results['errors'].append(f"Pit strategy error: {e}")
        
        return pit_strategies
    
    def save_results(self, work_dir: Path, predictions: dict, pit_strategies: dict) -> None:
        """
        Save processing results
        """
        logger.info("💾 Saving results...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'processing_results': self.processing_results,
            'predictions': predictions,
            'pit_strategies': pit_strategies
        }
        
        results_file = work_dir / 'judge_session_results.json'
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"  ✅ Results saved to {results_file}")
    
    def process_judge_data(self, input_path: Path) -> dict:
        """
        Main processing function for judge data
        """
        logger.info("🏁 JUDGE DATA PROCESSOR")
        logger.info("=" * 50)
        logger.info(f"Processing: {input_path}")
        logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Step 1: Load existing model
            if not self.load_existing_model():
                self.processing_results['status'] = 'failed'
                self.processing_results['errors'].append('Failed to load model')
                return self.processing_results
            
            # Step 2: Detect data format
            detection_result = self.detect_data_format(input_path)
            
            # Step 3: Extract data
            work_dir = self.extract_data(input_path, detection_result)
            
            # Step 4: Identify data files
            data_files = self.identify_data_files(work_dir)
            self.processing_results['files_processed'] = sum(len(files) for files in data_files.values())
            
            # Step 5: Process telemetry
            track_abbrev = detection_result['track']
            if track_abbrev == 'unknown':
                # Try to infer from data or use default
                track_abbrev = 'VIR'  # Default to VIR for unknown tracks
                self.processing_results['warnings'].append('Track not identified, using VIR as default')
            
            telemetry_df = self.process_telemetry_data(data_files['telemetry'], track_abbrev)
            
            # Step 6: Generate predictions
            predictions = self.generate_predictions(telemetry_df, track_abbrev)
            
            # Step 7: Generate pit strategy
            pit_strategies = self.generate_pit_strategy(predictions, track_abbrev)
            
            # Step 8: Save results
            self.save_results(work_dir, predictions, pit_strategies)
            
            # Update status
            self.processing_results['status'] = 'completed'
            self.processing_results['work_directory'] = str(work_dir)
            
            # Summary
            logger.info(f"\n📊 PROCESSING SUMMARY:")
            logger.info(f"  Status: {self.processing_results['status']}")
            logger.info(f"  Files processed: {self.processing_results['files_processed']}")
            logger.info(f"  Predictions generated: {self.processing_results['predictions_generated']}")
            logger.info(f"  Average confidence: {self.processing_results['confidence_level']:.1%}")
            logger.info(f"  Warnings: {len(self.processing_results['warnings'])}")
            logger.info(f"  Errors: {len(self.processing_results['errors'])}")
            
            if self.processing_results['confidence_level'] >= 0.8:
                logger.info(f"  🎯 VERDICT: HIGH CONFIDENCE - Ready for competition!")
            elif self.processing_results['confidence_level'] >= 0.6:
                logger.info(f"  🤔 VERDICT: MEDIUM CONFIDENCE - Usable with caution")
            else:
                logger.info(f"  ⚠️  VERDICT: LOW CONFIDENCE - Manual review recommended")
            
        except Exception as e:
            logger.error(f"❌ Processing failed: {e}")
            self.processing_results['status'] = 'failed'
            self.processing_results['errors'].append(str(e))
        
        return self.processing_results

def main():
    """
    Main function for command-line usage
    """
    parser = argparse.ArgumentParser(description='Process new GR Cup data for judges')
    parser.add_argument('--input', '-i', required=True, help='Input data path (ZIP, CSV, or directory)')
    parser.add_argument('--output', '-o', help='Output directory (optional)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    input_path = Path(args.input)
    
    if not input_path.exists():
        logger.error(f"Input path does not exist: {input_path}")
        return 1
    
    # Process the data
    processor = JudgeDataProcessor()
    results = processor.process_judge_data(input_path)
    
    # Return appropriate exit code
    if results['status'] == 'completed':
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())