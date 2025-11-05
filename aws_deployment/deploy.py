"""
AWS Deployment Script for GR Cup Analytics

This script handles the complete deployment of the GR Cup analytics platform to AWS.
"""

import boto3
import json
import os
import subprocess
import sys
from pathlib import Path
import pandas as pd

class GRCupDeployer:
    """
    Deploy GR Cup Analytics to AWS
    """
    
    def __init__(self, stage='dev', region='us-east-1'):
        self.stage = stage
        self.region = region
        self.bucket_name = f"gr-cup-data-{stage}"
        
        # AWS clients
        self.s3 = boto3.client('s3', region_name=region)
        self.cloudformation = boto3.client('cloudformation', region_name=region)
        
    def check_prerequisites(self):
        """Check if all prerequisites are installed"""
        print("🔍 Checking prerequisites...")
        
        # Check if serverless is installed
        try:
            result = subprocess.run(['serverless', '--version'], capture_output=True, text=True)
            print(f"✅ Serverless Framework: {result.stdout.strip()}")
        except FileNotFoundError:
            print("❌ Serverless Framework not found. Install with: npm install -g serverless")
            return False
        
        # Check AWS credentials
        try:
            sts = boto3.client('sts')
            identity = sts.get_caller_identity()
            print(f"✅ AWS Account: {identity['Account']}")
        except Exception as e:
            print(f"❌ AWS credentials not configured: {e}")
            return False
        
        return True
    
    def deploy_infrastructure(self):
        """Deploy the serverless infrastructure"""
        print("🚀 Deploying infrastructure...")
        
        # Change to deployment directory
        os.chdir('aws_deployment')
        
        try:
            # Deploy using serverless
            result = subprocess.run([
                'serverless', 'deploy', 
                '--stage', self.stage,
                '--region', self.region,
                '--verbose'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Infrastructure deployed successfully!")
                print(result.stdout)
                return True
            else:
                print(f"❌ Deployment failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Deployment error: {e}")
            return False
        finally:
            os.chdir('..')
    
    def upload_telemetry_data(self):
        """Upload existing telemetry data to S3"""
        print("📊 Uploading telemetry data...")
        
        data_dir = Path("data/cleaned")
        if not data_dir.exists():
            print("❌ No cleaned data found. Run data processing first.")
            return False
        
        try:
            # Upload each telemetry file
            for csv_file in data_dir.glob("*_telemetry_clean.csv"):
                key = f"processed-telemetry/{csv_file.name}"
                
                print(f"Uploading {csv_file.name}...")
                self.s3.upload_file(
                    str(csv_file),
                    self.bucket_name,
                    key,
                    ExtraArgs={'ContentType': 'text/csv'}
                )
            
            print("✅ Telemetry data uploaded successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return False
    
    def upload_analysis_results(self):
        """Upload analysis results and visualizations"""
        print("📈 Uploading analysis results...")
        
        analysis_dir = Path("telemetry_analysis")
        if not analysis_dir.exists():
            print("❌ No analysis results found. Run telemetry analysis first.")
            return False
        
        try:
            # Upload analysis files
            for file_path in analysis_dir.iterdir():
                if file_path.is_file():
                    key = f"analysis-results/{file_path.name}"
                    
                    # Determine content type
                    if file_path.suffix == '.png':
                        content_type = 'image/png'
                    elif file_path.suffix == '.json':
                        content_type = 'application/json'
                    elif file_path.suffix == '.csv':
                        content_type = 'text/csv'
                    else:
                        content_type = 'binary/octet-stream'
                    
                    print(f"Uploading {file_path.name}...")
                    self.s3.upload_file(
                        str(file_path),
                        self.bucket_name,
                        key,
                        ExtraArgs={'ContentType': content_type}
                    )
            
            print("✅ Analysis results uploaded successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return False
    
    def get_deployment_info(self):
        """Get deployment information"""
        print("📋 Getting deployment information...")
        
        try:
            # Get CloudFormation stack outputs
            stack_name = f"gr-cup-analytics-{self.stage}"
            
            response = self.cloudformation.describe_stacks(StackName=stack_name)
            stack = response['Stacks'][0]
            
            outputs = {}
            if 'Outputs' in stack:
                for output in stack['Outputs']:
                    outputs[output['OutputKey']] = output['OutputValue']
            
            # Get API Gateway URL
            api_url = None
            for output in stack.get('Outputs', []):
                if 'ServiceEndpoint' in output.get('OutputKey', ''):
                    api_url = output['OutputValue']
                    break
            
            deployment_info = {
                'stage': self.stage,
                'region': self.region,
                'bucket_name': self.bucket_name,
                'api_url': api_url,
                'dashboard_url': f"{api_url}/dashboard" if api_url else None,
                'stack_name': stack_name,
                'outputs': outputs
            }
            
            return deployment_info
            
        except Exception as e:
            print(f"❌ Error getting deployment info: {e}")
            return None
    
    def create_demo_data(self):
        """Create demo data for testing"""
        print("🎯 Creating demo data...")
        
        try:
            # Create a simple demo telemetry file
            demo_data = {
                'vehicle_id': ['GR86-DEMO-001'] * 100,
                'timestamp': range(1000, 1100),
                'lap': [1] * 50 + [2] * 50,
                'Speed': [120 + i*0.5 for i in range(100)],
                'pbrake_f': [0 if i % 10 != 0 else 80 for i in range(100)],
                'ath': [75 + i*0.2 for i in range(100)],
                'Steering_Angle': [0.1 * (i % 20 - 10) for i in range(100)],
                'accx_can': [0.5 + 0.1 * (i % 5) for i in range(100)],
                'accy_can': [0.3 + 0.1 * (i % 7) for i in range(100)],
                'track_name': ['Demo Track'] * 100,
                'track_id': ['DEMO'] * 100
            }
            
            demo_df = pd.DataFrame(demo_data)
            
            # Upload demo data
            demo_csv = demo_df.to_csv(index=False)
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key='processed-telemetry/DEMO_telemetry_clean.csv',
                Body=demo_csv,
                ContentType='text/csv'
            )
            
            print("✅ Demo data created successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Demo data creation failed: {e}")
            return False

def main():
    """Main deployment function"""
    print("🏁 GR Cup Analytics - AWS Deployment")
    print("=" * 50)
    
    # Get deployment parameters
    stage = input("Enter deployment stage (dev/prod) [dev]: ").strip() or 'dev'
    region = input("Enter AWS region [us-east-1]: ").strip() or 'us-east-1'
    
    deployer = GRCupDeployer(stage=stage, region=region)
    
    # Check prerequisites
    if not deployer.check_prerequisites():
        print("❌ Prerequisites not met. Please install required tools.")
        return
    
    # Deploy infrastructure
    if not deployer.deploy_infrastructure():
        print("❌ Infrastructure deployment failed.")
        return
    
    # Upload data
    print("\n📊 Data Upload Options:")
    print("1. Upload existing telemetry data")
    print("2. Create demo data")
    print("3. Skip data upload")
    
    choice = input("Select option [1]: ").strip() or '1'
    
    if choice == '1':
        deployer.upload_telemetry_data()
        deployer.upload_analysis_results()
    elif choice == '2':
        deployer.create_demo_data()
    
    # Get deployment info
    deployment_info = deployer.get_deployment_info()
    
    if deployment_info:
        print("\n✅ DEPLOYMENT COMPLETE!")
        print("=" * 30)
        print(f"🌐 API URL: {deployment_info['api_url']}")
        print(f"📊 Dashboard: {deployment_info['dashboard_url']}")
        print(f"🪣 S3 Bucket: {deployment_info['bucket_name']}")
        print(f"🏷️  Stage: {deployment_info['stage']}")
        print(f"🌍 Region: {deployment_info['region']}")
        
        # Save deployment info
        with open(f'deployment_info_{stage}.json', 'w') as f:
            json.dump(deployment_info, f, indent=2)
        
        print(f"\n💾 Deployment info saved to: deployment_info_{stage}.json")
        print("\n🎯 Next Steps:")
        print("1. Visit the dashboard URL to view analytics")
        print("2. Use the API endpoints to access telemetry data")
        print("3. Upload additional telemetry files to the S3 bucket")
    
    else:
        print("❌ Could not retrieve deployment information.")

if __name__ == "__main__":
    main()