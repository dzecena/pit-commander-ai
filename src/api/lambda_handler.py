"""
AWS Lambda function for serverless predictions

Author: GR Cup Analytics Team
Date: 2025-10-30

Handles:
- Tire degradation predictions
- Pit strategy recommendations
- Model serving from S3

Environment Variables:
- S3_BUCKET: Bucket containing models
- MODEL_VERSION: Model version to load
"""

import json
import joblib
import boto3
import logging
import os
from typing import Dict, Any
import numpy as np

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
s3 = boto3.client('s3')

# Global model variables (loaded once per container)
tire_model = None
scaler = None
model_loaded = False

# Configuration
S3_BUCKET = os.environ.get('S3_BUCKET', 'gr-cup-hackathon')
MODEL_VERSION = os.environ.get('MODEL_VERSION', 'v1')

def load_model():
    """
    Load model from S3 at cold start
    """
    global tire_model, scaler, model_loaded
    
    if model_loaded:
        return True
    
    try:
        logger.info("Loading model from S3...")
        
        # Download model files to /tmp
        model_key = f'models/tire_degradation_{MODEL_VERSION}.pkl'
        scaler_key = f'models/scaler_{MODEL_VERSION}.pkl'
        
        model_path = '/tmp/model.pkl'
        scaler_path = '/tmp/scaler.pkl'
        
        # Download from S3
        s3.download_file(S3_BUCKET, model_key, model_path)
        s3.download_file(S3_BUCKET, scaler_key, scaler_path)
        
        # Load models
        tire_model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        model_loaded = True
        logger.info("Model loaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return False

def extract_features(request_body: Dict[str, Any]) -> np.ndarray:
    """
    Extract and validate features from request
    """
    feature_names = [
        'tire_age',
        'driver_avg_pace',
        'track_avg_speed',
        'track_degradation_rate',
        'race_progress',
        'recent_pace_3lap',
        'session_best',
        'track_type_encoded'
    ]
    
    features = []
    
    for feature_name in feature_names:
        value = request_body.get(feature_name, 0.0)
        
        # Basic validation
        if feature_name == 'tire_age':
            value = max(1, min(30, int(value)))  # Clamp between 1-30
        elif feature_name == 'race_progress':
            value = max(0.0, min(1.0, float(value)))  # Clamp between 0-1
        else:
            value = float(value)
        
        features.append(value)
    
    return np.array(features).reshape(1, -1)

def lambda_handler(event, context):
    """
    Lambda entry point
    Event format: {
        'httpMethod': 'POST',
        'body': JSON string with prediction request,
        'path': '/predict/lap-time' or '/strategy/pit-window'
    }
    """
    logger.info(f"Lambda invoked with event: {json.dumps(event, default=str)}")
    
    try:
        # Load model if not already loaded
        if not load_model():
            return {
                'statusCode': 503,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({
                    'error': 'Model not available'
                })
            }
        
        # Handle CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': ''
            }
        
        # Parse request body
        if 'body' not in event:
            raise ValueError("No request body provided")
        
        body = json.loads(event['body'])
        path = event.get('path', '/predict/lap-time')
        
        # Route to appropriate handler
        if path == '/predict/lap-time':
            result = handle_lap_time_prediction(body)
        elif path == '/strategy/pit-window':
            result = handle_pit_strategy(body)
        elif path == '/health':
            result = handle_health_check()
        else:
            raise ValueError(f"Unknown path: {path}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Lambda error: {e}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'message': 'Internal server error'
            })
        }

def handle_lap_time_prediction(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle lap time prediction request
    """
    logger.info("Handling lap time prediction")
    
    # Extract features
    features = extract_features(body)
    
    # Scale features
    features_scaled = scaler.transform(features)
    
    # Make prediction
    prediction = tire_model.predict(features_scaled)[0]
    
    # Calculate confidence (simplified)
    confidence = 0.85  # Could be more sophisticated
    
    # Generate recommendation
    tire_age = body.get('tire_age', 1)
    if tire_age > 20:
        recommendation = "High tire degradation - consider pitting soon"
    elif tire_age > 15:
        recommendation = "Moderate tire degradation - monitor performance"
    else:
        recommendation = "Tires performing well"
    
    return {
        'predicted_time': float(prediction),
        'confidence': confidence,
        'recommendation': recommendation,
        'tire_age': tire_age,
        'model_version': MODEL_VERSION
    }

def handle_pit_strategy(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle pit strategy request (simplified version)
    """
    logger.info("Handling pit strategy request")
    
    current_lap = body.get('current_lap', 1)
    tire_age = body.get('tire_age', current_lap)
    max_laps = body.get('max_laps', 30)
    position = body.get('position', 5)
    
    # Simplified pit strategy logic
    if tire_age > 20:
        action = 'PIT_NOW'
        reasoning = 'Tires heavily degraded'
    elif tire_age > 15:
        laps_to_pit = min(3, max_laps - current_lap - 2)
        action = f'PIT_IN_{laps_to_pit}_LAPS'
        reasoning = f'Optimal window in {laps_to_pit} laps'
    else:
        action = 'STAY_OUT'
        reasoning = 'Tires still performing well'
    
    return {
        'action': action,
        'reasoning': reasoning,
        'current_lap': current_lap,
        'tire_age': tire_age,
        'position': position,
        'confidence': 0.7
    }

def handle_health_check() -> Dict[str, Any]:
    """
    Handle health check request
    """
    return {
        'status': 'healthy',
        'model_loaded': model_loaded,
        'model_version': MODEL_VERSION,
        's3_bucket': S3_BUCKET
    }

# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        'httpMethod': 'POST',
        'path': '/predict/lap-time',
        'body': json.dumps({
            'tire_age': 10,
            'driver_avg_pace': 120.5,
            'track_avg_speed': 160.0,
            'track_degradation_rate': 0.8,
            'race_progress': 0.4,
            'recent_pace_3lap': 121.0,
            'session_best': 118.5,
            'track_type_encoded': 1
        })
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))