"""
Configuration utilities for GR Cup Analytics

Author: GR Cup Analytics Team
Date: 2025-10-30
"""

import os
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Track configurations
TRACKS = {
    'BMP': {
        'name': 'Barber Motorsports Park',
        'folder': 'barber-motorsports-park',
        'typical_lap_time': 85.0,  # seconds
        'sectors': 6
    },
    'COTA': {
        'name': 'Circuit of the Americas',
        'folder': 'circuit-of-the-americas',
        'typical_lap_time': 125.0,
        'sectors': 6
    },
    'INDY': {
        'name': 'Indianapolis Motor Speedway',
        'folder': 'indianapolis',
        'typical_lap_time': 95.0,
        'sectors': 6
    },
    'RA': {
        'name': 'Road America',
        'folder': 'road-america',
        'typical_lap_time': 140.0,
        'sectors': 6
    },
    'SEB': {
        'name': 'Sebring International Raceway',
        'folder': 'sebring',
        'typical_lap_time': 130.0,
        'sectors': 6
    },
    'SON': {
        'name': 'Sonoma Raceway',
        'folder': 'sonoma',
        'typical_lap_time': 105.0,
        'sectors': 6
    },
    'VIR': {
        'name': 'Virginia International Raceway',
        'folder': 'virginia-international-raceway',
        'typical_lap_time': 115.0,
        'sectors': 6
    }
}

# Model configuration
MODEL_CONFIG = {
    'tire_degradation': {
        'features': [
            'tire_age',
            'driver_avg_pace', 
            'track_avg_speed',
            'track_degradation_rate',
            'race_progress',
            'recent_pace_3lap',
            'session_best',
            'track_type_encoded'
        ],
        'target_rmse': 0.5,
        'target_r2': 0.85
    }
}

# API configuration
API_CONFIG = {
    'host': '0.0.0.0',
    'port': int(os.getenv('API_PORT', 8000)),
    'websocket_port': int(os.getenv('WEBSOCKET_PORT', 8001)),
    'cors_origins': ['*']
}

# AWS configuration
AWS_CONFIG = {
    'region': os.getenv('AWS_REGION', 'us-east-1'),
    'bucket': os.getenv('S3_BUCKET_NAME', 'gr-cup-hackathon'),
    'lambda_memory': 512,
    'lambda_timeout': 30
}

# Data paths
DATA_PATHS = {
    'raw': Path('data/raw'),
    'extracted': Path('data/extracted'),
    'cleaned': Path('data/cleaned'),
    'models': Path('models')
}


def get_track_config(track_abbrev: str) -> Dict[str, Any]:
    """Get configuration for specific track"""
    return TRACKS.get(track_abbrev, {})


def get_data_path(path_type: str) -> Path:
    """Get data path by type"""
    return DATA_PATHS.get(path_type, Path('.'))


def setup_logging(level: str = 'INFO') -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def validate_environment() -> bool:
    """Validate required environment variables and paths"""
    required_paths = ['data/extracted', 'data/cleaned', 'models']
    
    for path in required_paths:
        Path(path).mkdir(parents=True, exist_ok=True)
    
    logger.info("Environment validation complete")
    return True