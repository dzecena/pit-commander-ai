"""
Recovery Check - Assess current state after interruption

Author: GR Cup Analytics Team
Date: 2025-10-30

This script checks what's been completed and what needs to be done
after a system interruption (blue screen, crash, etc.)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import sys
import json
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from utils.config import TRACKS, setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def check_project_structure():
    """
    Check if basic project structure exists
    """
    logger.info("🔍 Checking project structure...")
    
    required_dirs = [
        "data/raw",
        "data/extracted", 
        "data/cleaned",
        "models",
        "src/data_processing",
        "src/models",
        "src/api",
        "scripts",
        "templates"
    ]
    
    structure_status = {}
    
    for directory in required_dirs:
        path = Path(directory)
        exists = path.exists()
        structure_status[directory] = exists
        
        status = "✅" if exists else "❌"
        logger.info(f"  {status} {directory}")
    
    missing_dirs = [d for d, exists in structure_status.items() if not exists]
    
    if missing_dirs:
        logger.warning(f"Missing directories: {missing_dirs}")
        return False
    else:
        logger.info("✅ Project structure complete")
        return True

def check_dependencies():
    """
    Check if required Python packages are installed
    """
    logger.info("🔍 Checking Python dependencies...")
    
    required_packages = [
        'pandas', 'numpy', 'scikit-learn', 'matplotlib', 
        'seaborn', 'fastapi', 'uvicorn', 'requests', 'tqdm'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"  ✅ {package}")
        except ImportError:
            logger.info(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        logger.warning(f"Missing packages: {missing_packages}")
        logger.info("Install with: pip install " + " ".join(missing_packages))
        return False
    else:
        logger.info("✅ All dependencies installed")
        return True

def check_data_files():
    """
    Check status of data files
    """
    logger.info("🔍 Checking data files...")
    
    # Check raw data (ZIP files)
    raw_path = Path("data/raw")
    zip_files = list(raw_path.glob("*.zip")) if raw_path.exists() else []
    
    logger.info(f"📁 Raw data files ({len(zip_files)}):")
    expected_zips = [f"{track_folder}.zip" for track_folder in TRACKS.values()]
    
    for expected_zip in expected_zips:
        zip_path = raw_path / expected_zip
        if zip_path.exists():
            size_mb = zip_path.stat().st_size / (1024 * 1024)
            logger.info(f"  ✅ {expected_zip} ({size_mb:.1f} MB)")
        else:
            logger.info(f"  ❌ {expected_zip}")
    
    # Check extracted data
    extracted_path = Path("data/extracted")
    extracted_dirs = []
    if extracted_path.exists():
        extracted_dirs = [d for d in extracted_path.iterdir() if d.is_dir()]
    
    logger.info(f"📂 Extracted data ({len(extracted_dirs)} tracks):")
    for track_abbrev, track_config in TRACKS.items():
        track_folder = track_config['folder']
        track_path = extracted_path / track_folder
        if track_path.exists():
            csv_files = list(track_path.glob("*.csv"))
            logger.info(f"  ✅ {track_folder} ({len(csv_files)} CSV files)")
        else:
            logger.info(f"  ❌ {track_folder}")
    
    # Check cleaned data
    cleaned_path = Path("data/cleaned")
    cleaned_files = []
    if cleaned_path.exists():
        cleaned_files = list(cleaned_path.glob("*.csv"))
    
    logger.info(f"🧹 Cleaned data ({len(cleaned_files)} files):")
    for track_abbrev in TRACKS.keys():
        clean_file = cleaned_path / f"{track_abbrev}_telemetry_clean.csv"
        if clean_file.exists():
            try:
                df = pd.read_csv(clean_file, nrows=5)
                logger.info(f"  ✅ {track_abbrev}_telemetry_clean.csv ({len(df)} sample rows)")
            except Exception as e:
                logger.info(f"  ⚠️  {track_abbrev}_telemetry_clean.csv (error: {e})")
        else:
            logger.info(f"  ❌ {track_abbrev}_telemetry_clean.csv")
    
    return {
        'zip_files': len(zip_files),
        'extracted_dirs': len(extracted_dirs),
        'cleaned_files': len(cleaned_files)
    }

def check_models():
    """
    Check if ML models exist and are trained
    """
    logger.info("🔍 Checking ML models...")
    
    models_path = Path("models")
    
    # Check for model files
    model_files = {
        'tire_degradation_v1.pkl': models_path / 'tire_degradation_v1.pkl',
        'scaler_v1.pkl': models_path / 'scaler_v1.pkl',
        'training_metrics.json': models_path / 'training_metrics.json',
        'model_evaluation.png': models_path / 'model_evaluation.png'
    }
    
    model_status = {}
    
    for name, path in model_files.items():
        exists = path.exists()
        model_status[name] = exists
        
        status = "✅" if exists else "❌"
        logger.info(f"  {status} {name}")
        
        # Check model metrics if available
        if name == 'training_metrics.json' and exists:
            try:
                with open(path, 'r') as f:
                    metrics = json.load(f)
                
                test_r2 = metrics.get('test_r2', 0)
                test_rmse = metrics.get('test_rmse', 999)
                
                logger.info(f"    📊 Model R²: {test_r2:.3f}")
                logger.info(f"    📊 Model RMSE: {test_rmse:.3f}s")
                
                if test_r2 > 0.9:
                    logger.info("    🎯 Model performance: EXCELLENT")
                elif test_r2 > 0.8:
                    logger.info("    🎯 Model performance: GOOD")
                else:
                    logger.info("    🎯 Model performance: NEEDS IMPROVEMENT")
                    
            except Exception as e:
                logger.warning(f"    ⚠️  Could not read metrics: {e}")
    
    return model_status

def check_api_status():
    """
    Check if API components are ready
    """
    logger.info("🔍 Checking API status...")
    
    # Check if API files exist
    api_files = [
        "src/api/main.py",
        "src/api/lambda_handler.py"
    ]
    
    for api_file in api_files:
        path = Path(api_file)
        status = "✅" if path.exists() else "❌"
        logger.info(f"  {status} {api_file}")
    
    # Try to import API components
    try:
        sys.path.append("src")
        from api.main import app
        logger.info("  ✅ FastAPI app can be imported")
        api_ready = True
    except Exception as e:
        logger.info(f"  ❌ FastAPI import error: {e}")
        api_ready = False
    
    return api_ready

def generate_recovery_plan(data_status, model_status, api_ready):
    """
    Generate a recovery plan based on current status
    """
    logger.info("\n🚀 RECOVERY PLAN")
    logger.info("=" * 50)
    
    steps = []
    
    # Step 1: Data
    if data_status['zip_files'] == 0:
        steps.append({
            'step': 1,
            'action': 'Download data files',
            'command': 'python scripts/download_data.py',
            'description': 'Download all 7 track ZIP files from TRD portal'
        })
    
    if data_status['extracted_dirs'] < 7:
        steps.append({
            'step': len(steps) + 1,
            'action': 'Extract and process data',
            'command': 'python scripts/process_real_data.py',
            'description': 'Extract ZIP files and clean telemetry data'
        })
    
    # Step 2: Models
    if not model_status.get('tire_degradation_v1.pkl', False):
        steps.append({
            'step': len(steps) + 1,
            'action': 'Train ML model',
            'command': 'python scripts/train_model.py',
            'description': 'Train tire degradation model with real data'
        })
    
    # Step 3: Testing
    steps.append({
        'step': len(steps) + 1,
        'action': 'Test system',
        'command': 'python demo/race_demo.py',
        'description': 'Test predictions and pit strategy'
    })
    
    # Step 4: API
    if api_ready:
        steps.append({
            'step': len(steps) + 1,
            'action': 'Start API server',
            'command': 'uvicorn src.api.main:app --reload --port 8000',
            'description': 'Start prediction API server'
        })
    
    # Display plan
    for step in steps:
        logger.info(f"\n📋 Step {step['step']}: {step['action']}")
        logger.info(f"   Command: {step['command']}")
        logger.info(f"   Purpose: {step['description']}")
    
    return steps

def main():
    """
    Main recovery check function
    """
    logger.info("🏁 GR Cup Analytics - Recovery Check")
    logger.info("=" * 50)
    logger.info(f"Recovery started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    # Check each component
    structure_ok = check_project_structure()
    dependencies_ok = check_dependencies()
    data_status = check_data_files()
    model_status = check_models()
    api_ready = check_api_status()
    
    # Overall status
    logger.info(f"\n📊 OVERALL STATUS")
    logger.info("=" * 30)
    logger.info(f"Project Structure: {'✅' if structure_ok else '❌'}")
    logger.info(f"Dependencies: {'✅' if dependencies_ok else '❌'}")
    logger.info(f"Data Files: {data_status['zip_files']}/7 ZIP, {data_status['extracted_dirs']}/7 extracted, {data_status['cleaned_files']} cleaned")
    logger.info(f"ML Models: {'✅' if model_status.get('tire_degradation_v1.pkl') else '❌'}")
    logger.info(f"API Ready: {'✅' if api_ready else '❌'}")
    
    # Generate recovery plan
    recovery_steps = generate_recovery_plan(data_status, model_status, api_ready)
    
    # Quick start recommendation
    logger.info(f"\n🎯 QUICK START RECOMMENDATION:")
    
    if data_status['zip_files'] == 0:
        logger.info("Start with downloading data:")
        logger.info("  python scripts/download_data.py")
    elif data_status['cleaned_files'] == 0:
        logger.info("Start with processing existing data:")
        logger.info("  python scripts/process_real_data.py")
    elif not model_status.get('tire_degradation_v1.pkl'):
        logger.info("Start with training the model:")
        logger.info("  python scripts/train_model.py")
    else:
        logger.info("System looks good! Test it:")
        logger.info("  python demo/race_demo.py")
    
    logger.info(f"\n✅ Recovery check complete!")
    
    return True

if __name__ == "__main__":
    main()