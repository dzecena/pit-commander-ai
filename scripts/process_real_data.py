"""
Process real GR Cup data from ZIP files

Author: GR Cup Analytics Team
Date: 2025-10-30

This script:
1. Extracts ZIP files from data/raw/
2. Organizes data by track
3. Cleans and processes telemetry data
4. Generates analysis reports
"""

import zipfile
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import sys
import shutil
import glob

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from data_processing.multi_track_loader import MultiTrackLoader
from data_processing.data_cleaner import GRCupDataCleaner
from data_processing.sector_parser import SectorAnalyzer
from utils.config import TRACKS, setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def extract_zip_files():
    """
    Extract all ZIP files from data/raw/ to data/extracted/
    """
    raw_path = Path("data/raw")
    extracted_path = Path("data/extracted")
    
    logger.info("Extracting ZIP files...")
    
    # Find all ZIP files
    zip_files = list(raw_path.glob("*.zip"))
    
    if not zip_files:
        logger.warning("No ZIP files found in data/raw/")
        logger.info("Please place your track ZIP files in data/raw/")
        return False
    
    logger.info(f"Found {len(zip_files)} ZIP files")
    
    for zip_file in zip_files:
        logger.info(f"Extracting {zip_file.name}...")
        
        # Determine track folder name
        track_folder = zip_file.stem.lower().replace(' ', '-').replace('_', '-')
        
        # Map to our standard track folders
        folder_mapping = {
            'barber': 'barber-motorsports-park',
            'cota': 'circuit-of-the-americas',
            'circuit-of-the-americas': 'circuit-of-the-americas',
            'indianapolis': 'indianapolis',
            'indy': 'indianapolis',
            'road-america': 'road-america',
            'sebring': 'sebring',
            'sonoma': 'sonoma',
            'vir': 'virginia-international-raceway',
            'virginia': 'virginia-international-raceway'
        }
        
        # Find matching folder
        target_folder = None
        for key, value in folder_mapping.items():
            if key in track_folder:
                target_folder = value
                break
        
        if not target_folder:
            logger.warning(f"Could not map {zip_file.name} to a track folder")
            target_folder = track_folder
        
        extract_dir = extracted_path / target_folder
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            logger.info(f"Extracted to {extract_dir}")
            
        except Exception as e:
            logger.error(f"Error extracting {zip_file}: {e}")
    
    return True

def analyze_extracted_data():
    """
    Analyze the structure of extracted data
    """
    logger.info("Analyzing extracted data structure...")
    
    extracted_path = Path("data/extracted")
    
    for track_folder in extracted_path.iterdir():
        if not track_folder.is_dir():
            continue
        
        logger.info(f"\n📁 {track_folder.name}:")
        
        # List all files
        files = list(track_folder.rglob("*"))
        csv_files = [f for f in files if f.suffix.lower() == '.csv']
        
        logger.info(f"  Total files: {len(files)}")
        logger.info(f"  CSV files: {len(csv_files)}")
        
        # Analyze CSV files
        for csv_file in csv_files[:5]:  # Show first 5 CSV files
            try:
                df = pd.read_csv(csv_file, nrows=5)  # Read just first 5 rows
                logger.info(f"  📊 {csv_file.name}: {len(df.columns)} columns, shape preview: {df.shape}")
                logger.info(f"     Columns: {list(df.columns)[:10]}...")  # First 10 columns
            except Exception as e:
                logger.warning(f"  ❌ {csv_file.name}: Error reading - {e}")

def identify_file_types():
    """
    Identify telemetry, lap times, sector data, and results files
    """
    logger.info("Identifying file types...")
    
    extracted_path = Path("data/extracted")
    file_types = {
        'telemetry': [],
        'lap_times': [],
        'sectors': [],
        'results': [],
        'unknown': []
    }
    
    # Keywords to identify file types
    telemetry_keywords = ['telemetry', 'data', 'raw', 'sensor']
    lap_keywords = ['lap', 'time', 'timing']
    sector_keywords = ['sector', 'analysis', 'endurance', 'split']
    result_keywords = ['result', 'final', 'position', 'classification']
    
    for track_folder in extracted_path.iterdir():
        if not track_folder.is_dir():
            continue
        
        csv_files = list(track_folder.rglob("*.csv"))
        
        for csv_file in csv_files:
            filename_lower = csv_file.name.lower()
            
            # Classify file
            if any(keyword in filename_lower for keyword in telemetry_keywords):
                file_types['telemetry'].append(csv_file)
            elif any(keyword in filename_lower for keyword in lap_keywords):
                file_types['lap_times'].append(csv_file)
            elif any(keyword in filename_lower for keyword in sector_keywords):
                file_types['sectors'].append(csv_file)
            elif any(keyword in filename_lower for keyword in result_keywords):
                file_types['results'].append(csv_file)
            else:
                file_types['unknown'].append(csv_file)
    
    # Report findings
    for file_type, files in file_types.items():
        logger.info(f"\n{file_type.upper()} files ({len(files)}):")
        for file in files[:3]:  # Show first 3 of each type
            logger.info(f"  📄 {file.parent.name}/{file.name}")
        if len(files) > 3:
            logger.info(f"  ... and {len(files) - 3} more")
    
    return file_types

def process_real_telemetry():
    """
    Process real telemetry data using our existing pipeline
    """
    logger.info("Processing real telemetry data...")
    
    # Use our existing multi-track loader
    loader = MultiTrackLoader()
    
    try:
        # Load all tracks
        tracks_data = loader.load_all_tracks()
        
        if not tracks_data:
            logger.error("No track data loaded from real files")
            return False
        
        logger.info(f"Successfully loaded {len(tracks_data)} tracks")
        
        # Generate track summary
        summary_df = loader.get_track_summary()
        
        if not summary_df.empty:
            logger.info("\n📊 TRACK SUMMARY:")
            for _, row in summary_df.iterrows():
                logger.info(f"  🏁 {row['track']}: {row['total_laps']} laps, "
                          f"avg {row['avg_lap_time']:.1f}s, {row['track_type']}")
        
        # Compare tire degradation
        degradation_df = loader.compare_tire_degradation()
        
        if not degradation_df.empty:
            logger.info("\n🔥 TIRE DEGRADATION COMPARISON:")
            degradation_sorted = degradation_df.sort_values('degradation_rate', ascending=False)
            for _, row in degradation_sorted.iterrows():
                logger.info(f"  🏁 {row['track']}: +{row['degradation_rate']:.2f}s/stint "
                          f"({row['pct_increase']:.1f}% increase)")
        
        # Save combined dataset
        combined_df = loader.save_combined_dataset()
        
        if not combined_df.empty:
            logger.info(f"\n💾 Saved combined dataset: {len(combined_df)} records")
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing real telemetry: {e}")
        return False

def generate_data_quality_report():
    """
    Generate a comprehensive data quality report
    """
    logger.info("Generating data quality report...")
    
    report = {
        'tracks_processed': 0,
        'total_records': 0,
        'lap_errors_fixed': 0,
        'timestamp_corrections': 0,
        'data_quality_issues': []
    }
    
    cleaned_path = Path("data/cleaned")
    
    # Analyze cleaned data
    for stats_file in cleaned_path.glob("*_cleaning_stats.json"):
        try:
            import json
            with open(stats_file, 'r') as f:
                stats = json.load(f)
            
            report['tracks_processed'] += 1
            report['total_records'] += stats.get('total_records', 0)
            report['lap_errors_fixed'] += stats.get('lap_errors_fixed', 0)
            report['timestamp_corrections'] += stats.get('timestamp_corrections', 0)
            
        except Exception as e:
            logger.warning(f"Could not read {stats_file}: {e}")
    
    # Generate report
    logger.info(f"\n📋 DATA QUALITY REPORT:")
    logger.info(f"  Tracks Processed: {report['tracks_processed']}")
    logger.info(f"  Total Records: {report['total_records']:,}")
    logger.info(f"  Lap Errors Fixed: {report['lap_errors_fixed']:,}")
    logger.info(f"  Timestamp Corrections: {report['timestamp_corrections']:,}")
    
    # Save report
    report_path = Path("data/cleaned/data_quality_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"  Report saved to: {report_path}")
    
    return report

def main():
    """
    Main processing pipeline for real GR Cup data
    """
    logger.info("🏁 Processing Real GR Cup Data")
    logger.info("=" * 50)
    
    # Step 1: Extract ZIP files
    if not extract_zip_files():
        logger.error("Failed to extract ZIP files")
        return
    
    # Step 2: Analyze data structure
    analyze_extracted_data()
    
    # Step 3: Identify file types
    file_types = identify_file_types()
    
    # Step 4: Process telemetry data
    if not process_real_telemetry():
        logger.error("Failed to process telemetry data")
        return
    
    # Step 5: Generate quality report
    report = generate_data_quality_report()
    
    logger.info("\n✅ REAL DATA PROCESSING COMPLETE!")
    logger.info("\nNext steps:")
    logger.info("1. Review the data quality report")
    logger.info("2. Retrain the model with real data:")
    logger.info("   python scripts/train_model.py")
    logger.info("3. Test the API with real predictions:")
    logger.info("   python demo/race_demo.py")
    
    return True

if __name__ == "__main__":
    main()