#!/usr/bin/env python3
"""
Dashboard Version Manager for GR Cup Analytics

This script helps manage dashboard versions for easy rollback and tracking.
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path

class DashboardVersionManager:
    def __init__(self):
        self.dashboard_dir = Path("dashboard")
        self.versions_dir = self.dashboard_dir / "versions"
        self.versions_dir.mkdir(exist_ok=True)
        self.version_log = self.versions_dir / "version_log.json"
        
    def create_version(self, version_name, description="", is_working=True):
        """Create a new version of the dashboard"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create version filename
        status = "working" if is_working else "broken"
        version_filename = f"track_dashboard_{version_name}_{status}_{timestamp}.html"
        version_path = self.versions_dir / version_filename
        
        # Copy current dashboard
        current_dashboard = self.dashboard_dir / "track_dashboard.html"
        if current_dashboard.exists():
            shutil.copy2(current_dashboard, version_path)
            
            # Update version log
            self._update_version_log(version_name, version_filename, description, is_working, timestamp)
            
            print(f"✅ Created version: {version_filename}")
            print(f"📝 Description: {description}")
            return version_path
        else:
            print("❌ Current dashboard not found!")
            return None
    
    def list_versions(self):
        """List all available versions"""
        if not self.version_log.exists():
            print("📋 No versions found.")
            return
            
        with open(self.version_log, 'r') as f:
            versions = json.load(f)
        
        print("📋 Available Dashboard Versions:")
        print("=" * 50)
        
        for version in sorted(versions, key=lambda x: x['timestamp'], reverse=True):
            status_icon = "✅" if version['is_working'] else "❌"
            print(f"{status_icon} {version['version_name']} ({version['timestamp']})")
            print(f"   📁 File: {version['filename']}")
            print(f"   📝 Description: {version['description']}")
            print()
    
    def rollback_to_version(self, version_name):
        """Rollback to a specific version"""
        if not self.version_log.exists():
            print("❌ No version log found!")
            return False
            
        with open(self.version_log, 'r') as f:
            versions = json.load(f)
        
        # Find the version
        target_version = None
        for version in versions:
            if version['version_name'] == version_name:
                target_version = version
                break
        
        if not target_version:
            print(f"❌ Version '{version_name}' not found!")
            return False
        
        # Check if version file exists
        version_file = self.versions_dir / target_version['filename']
        if not version_file.exists():
            print(f"❌ Version file not found: {target_version['filename']}")
            return False
        
        # Backup current version first
        self.create_version("backup_before_rollback", f"Auto-backup before rolling back to {version_name}", False)
        
        # Copy version to current dashboard
        current_dashboard = self.dashboard_dir / "track_dashboard.html"
        shutil.copy2(version_file, current_dashboard)
        
        print(f"✅ Rolled back to version: {version_name}")
        print(f"📁 Restored from: {target_version['filename']}")
        return True
    
    def deploy_current_version(self, s3_bucket="gr-cup-data-dev-us-east-1-v2"):
        """Deploy current dashboard version to S3"""
        import subprocess
        
        current_dashboard = self.dashboard_dir / "track_dashboard.html"
        if not current_dashboard.exists():
            print("❌ Current dashboard not found!")
            return False
        
        try:
            # Upload to S3
            cmd = f"aws s3 cp {current_dashboard} s3://{s3_bucket}/dashboard/track_dashboard.html"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Dashboard deployed to S3 successfully!")
                print(f"🌐 Live URL: https://{s3_bucket}.s3.amazonaws.com/dashboard/track_dashboard.html")
                return True
            else:
                print(f"❌ Deployment failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Deployment error: {e}")
            return False
    
    def _update_version_log(self, version_name, filename, description, is_working, timestamp):
        """Update the version log file"""
        versions = []
        
        if self.version_log.exists():
            with open(self.version_log, 'r') as f:
                versions = json.load(f)
        
        # Add new version
        versions.append({
            "version_name": version_name,
            "filename": filename,
            "description": description,
            "is_working": is_working,
            "timestamp": timestamp,
            "created_at": datetime.now().isoformat()
        })
        
        # Save updated log
        with open(self.version_log, 'w') as f:
            json.dump(versions, f, indent=2)

def main():
    import sys
    
    manager = DashboardVersionManager()
    
    if len(sys.argv) < 2:
        print("🏁 GR Cup Dashboard Version Manager")
        print("=" * 40)
        print("Usage:")
        print("  python version_manager.py create <version_name> [description]")
        print("  python version_manager.py list")
        print("  python version_manager.py rollback <version_name>")
        print("  python version_manager.py deploy")
        print()
        print("Examples:")
        print("  python version_manager.py create v1.1 'Added real data integration'")
        print("  python version_manager.py rollback v1.0")
        return
    
    command = sys.argv[1]
    
    if command == "create":
        if len(sys.argv) < 3:
            print("❌ Version name required!")
            return
        version_name = sys.argv[2]
        description = sys.argv[3] if len(sys.argv) > 3 else ""
        manager.create_version(version_name, description)
        
    elif command == "list":
        manager.list_versions()
        
    elif command == "rollback":
        if len(sys.argv) < 3:
            print("❌ Version name required!")
            return
        version_name = sys.argv[2]
        manager.rollback_to_version(version_name)
        
    elif command == "deploy":
        manager.deploy_current_version()
        
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()