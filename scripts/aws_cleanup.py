"""
AWS Cleanup Script for GR Cup Analytics

This script safely removes all AWS resources to avoid ongoing costs
when the competition season ends or for temporary shutdowns.

IMPORTANT: This will delete all data and infrastructure!
Make sure to backup any important data before running.
"""

import boto3
import json
import subprocess
from pathlib import Path
from datetime import datetime
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GRCupAWSCleanup:
    """
    Comprehensive AWS resource cleanup for GR Cup Analytics
    """
    
    def __init__(self, stage='dev', region='us-east-1'):
        self.stage = stage
        self.region = region
        self.stack_name = f"gr-cup-analytics-{stage}"
        self.bucket_name = f"gr-cup-data-{stage}-{region}-v2"
        
        # AWS clients
        self.s3 = boto3.client('s3', region_name=region)
        self.cloudformation = boto3.client('cloudformation', region_name=region)
        self.dynamodb = boto3.client('dynamodb', region_name=region)
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.apigateway = boto3.client('apigateway', region_name=region)
        
        self.cleanup_report = {
            'cleanup_date': datetime.now().isoformat(),
            'stage': stage,
            'region': region,
            'resources_removed': [],
            'errors': [],
            'cost_savings': {}
        }
    
    def confirm_cleanup(self):
        """
        Get user confirmation before proceeding with cleanup
        """
        print("🚨 AWS CLEANUP WARNING 🚨")
        print("=" * 50)
        print("This will PERMANENTLY DELETE all GR Cup Analytics resources:")
        print(f"• CloudFormation Stack: {self.stack_name}")
        print(f"• S3 Bucket: {self.bucket_name} (and ALL data)")
        print(f"• DynamoDB Tables: gr-cup-telemetry-{self.stage}")
        print(f"• Lambda Functions: All analytics functions")
        print(f"• API Gateway: All endpoints")
        print(f"• Stage: {self.stage}")
        print(f"• Region: {self.region}")
        print()
        print("💰 This cleanup will STOP all ongoing AWS charges!")
        print("⚠️  Make sure to backup any important data first!")
        print()
        
        # Double confirmation
        confirm1 = input("Type 'DELETE' to confirm cleanup: ").strip()
        if confirm1 != 'DELETE':
            print("❌ Cleanup cancelled.")
            return False
        
        confirm2 = input(f"Type '{self.stage}' to confirm stage: ").strip()
        if confirm2 != self.stage:
            print("❌ Stage confirmation failed. Cleanup cancelled.")
            return False
        
        print("✅ Cleanup confirmed. Starting resource removal...")
        return True
    
    def backup_important_data(self):
        """
        Create backup of important configuration and baseline data
        """
        logger.info("💾 Creating backup of important data...")
        
        backup_dir = Path(f"backup_{self.stage}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        backup_dir.mkdir(exist_ok=True)
        
        try:
            # Backup deployment info
            if Path('deployment_info.json').exists():
                import shutil
                shutil.copy('deployment_info.json', backup_dir / 'deployment_info.json')
                logger.info("✅ Backed up deployment info")
            
            # Backup baselines
            baseline_dir = Path('data/baselines')
            if baseline_dir.exists():
                import shutil
                shutil.copytree(baseline_dir, backup_dir / 'baselines')
                logger.info("✅ Backed up performance baselines")
            
            # Backup serverless config
            serverless_config = Path('aws_deployment/serverless.yml')
            if serverless_config.exists():
                import shutil
                shutil.copy(serverless_config, backup_dir / 'serverless.yml')
                logger.info("✅ Backed up serverless configuration")
            
            self.cleanup_report['backup_location'] = str(backup_dir)
            logger.info(f"📁 Backup created at: {backup_dir}")
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            self.cleanup_report['errors'].append(f"Backup failed: {e}")
    
    def empty_s3_bucket(self):
        """
        Empty S3 bucket before deletion (required for bucket deletion)
        """
        logger.info(f"🗑️ Emptying S3 bucket: {self.bucket_name}")
        
        try:
            # Check if bucket exists
            self.s3.head_bucket(Bucket=self.bucket_name)
            
            # List and delete all objects
            paginator = self.s3.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket_name)
            
            objects_deleted = 0
            for page in pages:
                if 'Contents' in page:
                    objects = [{'Key': obj['Key']} for obj in page['Contents']]
                    if objects:
                        self.s3.delete_objects(
                            Bucket=self.bucket_name,
                            Delete={'Objects': objects}
                        )
                        objects_deleted += len(objects)
            
            logger.info(f"✅ Deleted {objects_deleted} objects from S3 bucket")
            self.cleanup_report['resources_removed'].append(f"S3 objects: {objects_deleted}")
            
        except self.s3.exceptions.NoSuchBucket:
            logger.info("ℹ️ S3 bucket doesn't exist, skipping")
        except Exception as e:
            logger.error(f"❌ Error emptying S3 bucket: {e}")
            self.cleanup_report['errors'].append(f"S3 cleanup error: {e}")
    
    def remove_serverless_stack(self):
        """
        Remove the entire Serverless Framework stack
        """
        logger.info("🗑️ Removing Serverless Framework stack...")
        
        try:
            # Use Serverless Framework to remove stack
            result = subprocess.run([
                'serverless', 'remove',
                '--stage', self.stage,
                '--region', self.region
            ], capture_output=True, text=True, cwd='aws_deployment', timeout=300)
            
            if result.returncode == 0:
                logger.info("✅ Serverless stack removed successfully")
                self.cleanup_report['resources_removed'].append("Serverless Framework stack")
                
                # Parse removed resources from output
                removed_resources = []
                for line in result.stdout.split('\n'):
                    if 'Removing' in line or 'Deleted' in line:
                        removed_resources.append(line.strip())
                
                self.cleanup_report['resources_removed'].extend(removed_resources)
                
            else:
                logger.error(f"❌ Serverless removal failed: {result.stderr}")
                self.cleanup_report['errors'].append(f"Serverless removal failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("⏰ Serverless removal timed out")
            self.cleanup_report['errors'].append("Serverless removal timed out")
        except Exception as e:
            logger.error(f"❌ Error removing serverless stack: {e}")
            self.cleanup_report['errors'].append(f"Serverless removal error: {e}")
    
    def cleanup_remaining_resources(self):
        """
        Clean up any remaining resources that might not be in the stack
        """
        logger.info("🧹 Cleaning up any remaining resources...")
        
        # Check for orphaned Lambda functions
        try:
            functions = self.lambda_client.list_functions()
            gr_cup_functions = [f for f in functions['Functions'] 
                              if 'gr-cup' in f['FunctionName'].lower()]
            
            for func in gr_cup_functions:
                try:
                    self.lambda_client.delete_function(FunctionName=func['FunctionName'])
                    logger.info(f"✅ Deleted orphaned Lambda: {func['FunctionName']}")
                    self.cleanup_report['resources_removed'].append(f"Lambda: {func['FunctionName']}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not delete Lambda {func['FunctionName']}: {e}")
                    
        except Exception as e:
            logger.warning(f"⚠️ Error checking Lambda functions: {e}")
        
        # Check for orphaned DynamoDB tables
        try:
            tables = self.dynamodb.list_tables()
            gr_cup_tables = [t for t in tables['TableNames'] 
                           if 'gr-cup' in t.lower()]
            
            for table in gr_cup_tables:
                try:
                    self.dynamodb.delete_table(TableName=table)
                    logger.info(f"✅ Deleted orphaned DynamoDB table: {table}")
                    self.cleanup_report['resources_removed'].append(f"DynamoDB: {table}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not delete table {table}: {e}")
                    
        except Exception as e:
            logger.warning(f"⚠️ Error checking DynamoDB tables: {e}")
    
    def estimate_cost_savings(self):
        """
        Estimate monthly cost savings from cleanup
        """
        logger.info("💰 Estimating cost savings...")
        
        # Rough AWS cost estimates (monthly)
        cost_estimates = {
            'Lambda': 5.00,      # $5/month for moderate usage
            'API Gateway': 10.00, # $10/month for API calls
            'S3': 15.00,         # $15/month for storage and requests
            'DynamoDB': 5.00,    # $5/month for pay-per-request
            'CloudWatch': 2.00,  # $2/month for logs and metrics
            'Data Transfer': 3.00 # $3/month for data transfer
        }
        
        total_savings = sum(cost_estimates.values())
        
        self.cleanup_report['cost_savings'] = {
            'estimated_monthly_savings': total_savings,
            'breakdown': cost_estimates,
            'currency': 'USD'
        }
        
        logger.info(f"💰 Estimated monthly savings: ${total_savings:.2f}")
    
    def generate_cleanup_report(self):
        """
        Generate comprehensive cleanup report
        """
        logger.info("📋 Generating cleanup report...")
        
        report_file = f"cleanup_report_{self.stage}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(self.cleanup_report, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 50)
        print("🏁 GR Cup Analytics - Cleanup Complete!")
        print("=" * 50)
        print(f"📅 Cleanup Date: {self.cleanup_report['cleanup_date']}")
        print(f"🏷️ Stage: {self.stage}")
        print(f"🌍 Region: {self.region}")
        print()
        print("✅ Resources Removed:")
        for resource in self.cleanup_report['resources_removed']:
            print(f"  • {resource}")
        
        if self.cleanup_report['errors']:
            print("\n⚠️ Errors Encountered:")
            for error in self.cleanup_report['errors']:
                print(f"  • {error}")
        
        print(f"\n💰 Estimated Monthly Savings: ${self.cleanup_report['cost_savings']['estimated_monthly_savings']:.2f}")
        
        if 'backup_location' in self.cleanup_report:
            print(f"💾 Backup Location: {self.cleanup_report['backup_location']}")
        
        print(f"📋 Full Report: {report_file}")
        print("\n🎯 All AWS charges for GR Cup Analytics have been stopped!")
        print("To redeploy later, run the Core Deployment Notebook again.")
    
    def run_cleanup(self):
        """
        Execute complete cleanup process
        """
        if not self.confirm_cleanup():
            return False
        
        print("\n🧹 Starting AWS cleanup process...")
        print("=" * 40)
        
        # Step 1: Backup important data
        self.backup_important_data()
        
        # Step 2: Empty S3 bucket
        self.empty_s3_bucket()
        
        # Step 3: Remove Serverless stack
        self.remove_serverless_stack()
        
        # Step 4: Clean up remaining resources
        self.cleanup_remaining_resources()
        
        # Step 5: Estimate cost savings
        self.estimate_cost_savings()
        
        # Step 6: Generate report
        self.generate_cleanup_report()
        
        return True

def main():
    """
    Main cleanup function with user interaction
    """
    print("🏁 GR Cup Analytics - AWS Cleanup Tool")
    print("=" * 45)
    print()
    
    # Get cleanup parameters
    stage = input("Enter deployment stage to cleanup [dev]: ").strip() or 'dev'
    region = input("Enter AWS region [us-east-1]: ").strip() or 'us-east-1'
    
    print(f"\n🎯 Cleanup Configuration:")
    print(f"Stage: {stage}")
    print(f"Region: {region}")
    print()
    
    # Initialize and run cleanup
    cleanup = GRCupAWSCleanup(stage=stage, region=region)
    
    success = cleanup.run_cleanup()
    
    if success:
        print("\n✅ Cleanup completed successfully!")
        print("💰 All AWS charges have been stopped.")
        print("🔄 To redeploy, run the Core Deployment Notebook again.")
    else:
        print("\n❌ Cleanup was cancelled or failed.")
        print("💡 Check the error messages above for details.")

if __name__ == "__main__":
    main()