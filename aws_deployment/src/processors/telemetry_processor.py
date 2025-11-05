"""
Telemetry Data Processor - Process uploaded telemetry files
"""

import json
import boto3
import pandas as pd
from io import StringIO
import os

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Process telemetry files uploaded to S3
    """
    
    try:
        # Get bucket and key from S3 event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        
        print(f"Processing file: {key} from bucket: {bucket}")
        
        # Download the file
        response = s3_client.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        
        # Parse CSV
        df = pd.read_csv(StringIO(content))
        
        # Extract track information
        track_id = df['track_id'].iloc[0] if 'track_id' in df.columns else 'UNKNOWN'
        
        # Process and clean data
        processed_df = process_telemetry_data(df)
        
        # Save processed data back to S3
        processed_key = key.replace('raw-telemetry/', 'processed-telemetry/')
        processed_csv = processed_df.to_csv(index=False)
        
        s3_client.put_object(
            Bucket=bucket,
            Key=processed_key,
            Body=processed_csv,
            ContentType='text/csv'
        )
        
        # Update metadata in DynamoDB
        table_name = f"gr-cup-telemetry-{os.getenv('STAGE', 'dev')}"
        table = dynamodb.Table(table_name)
        
        table.put_item(
            Item={
                'track_id': track_id,
                'timestamp': context.aws_request_id,
                'file_key': processed_key,
                'total_laps': int(processed_df['lap'].nunique()),
                'data_points': len(processed_df),
                'max_speed': float(processed_df['Speed'].max()),
                'processed_at': context.aws_request_id
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Telemetry processed successfully',
                'track_id': track_id,
                'processed_key': processed_key,
                'data_points': len(processed_df)
            })
        }
        
    except Exception as e:
        print(f"Error processing telemetry: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

def process_telemetry_data(df):
    """
    Clean and process telemetry data
    """
    
    # Remove any null values
    df = df.dropna()
    
    # Ensure numeric columns are properly typed
    numeric_columns = ['Speed', 'pbrake_f', 'ath', 'Steering_Angle', 'accx_can', 'accy_can', 'nmotor']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Calculate additional metrics if not present
    if 'braking_intensity' not in df.columns:
        df['braking_intensity'] = df['pbrake_f'] / 100.0
    
    if 'cornering_force' not in df.columns:
        df['cornering_force'] = (df['accx_can']**2 + df['accy_can']**2)**0.5
    
    if 'throttle_efficiency' not in df.columns:
        df['throttle_efficiency'] = df['ath'] / 100.0
    
    # Sort by lap and timestamp
    df = df.sort_values(['lap', 'timestamp'])
    
    return df