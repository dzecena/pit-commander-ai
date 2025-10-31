"""
Download GR Cup data files from TRD hackathon portal

Author: GR Cup Analytics Team
Date: 2025-10-30

Downloads all track data ZIP files from the official TRD portal
"""

import requests
from pathlib import Path
import logging
import sys
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Official TRD data URLs
DATA_URLS = {
    'barber-motorsports-park': 'https://trddev.com/hackathon-2025/barber-motorsports-park.zip',
    'circuit-of-the-americas': 'https://trddev.com/hackathon-2025/circuit-of-the-americas.zip',
    'indianapolis': 'https://trddev.com/hackathon-2025/indianapolis.zip',
    'road-america': 'https://trddev.com/hackathon-2025/road-america.zip',
    'sebring': 'https://trddev.com/hackathon-2025/sebring.zip',
    'sonoma': 'https://trddev.com/hackathon-2025/sonoma.zip',
    'virginia-international-raceway': 'https://trddev.com/hackathon-2025/virginia-international-raceway.zip'
}

def create_directories():
    """
    Create necessary directories
    """
    directories = [
        Path("data/raw"),
        Path("Track Maps"),
        Path("Data Files")
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Created directory: {directory}")

def download_file(url: str, filepath: Path) -> bool:
    """
    Download a file with progress bar
    """
    try:
        logger.info(f"📥 Downloading: {filepath.name}")
        
        # Check if file already exists
        if filepath.exists():
            logger.info(f"⚠️  File already exists: {filepath.name}")
            response = input(f"Overwrite {filepath.name}? (y/n): ")
            if response.lower() != 'y':
                logger.info("Skipping download")
                return True
        
        # Start download
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get file size for progress bar
        total_size = int(response.headers.get('content-length', 0))
        
        with open(filepath, 'wb') as file, tqdm(
            desc=filepath.name,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    progress_bar.update(len(chunk))
        
        logger.info(f"✅ Downloaded: {filepath.name} ({total_size / (1024*1024):.1f} MB)")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Download failed for {filepath.name}: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error downloading {filepath.name}: {e}")
        return False

def verify_downloads():
    """
    Verify all downloads completed successfully
    """
    logger.info("🔍 Verifying downloads...")
    
    raw_path = Path("data/raw")
    expected_files = [f"{track}.zip" for track in DATA_URLS.keys()]
    
    missing_files = []
    corrupted_files = []
    total_size = 0
    
    for filename in expected_files:
        filepath = raw_path / filename
        
        if not filepath.exists():
            missing_files.append(filename)
        else:
            # Check file size (should be > 1MB for real data)
            file_size = filepath.stat().st_size
            total_size += file_size
            
            if file_size < 1024 * 1024:  # Less than 1MB
                corrupted_files.append(filename)
    
    # Report results
    if missing_files:
        logger.error(f"❌ Missing files: {missing_files}")
    
    if corrupted_files:
        logger.error(f"❌ Possibly corrupted files (too small): {corrupted_files}")
    
    if not missing_files and not corrupted_files:
        logger.info(f"✅ All downloads verified successfully!")
        logger.info(f"📊 Total download size: {total_size / (1024*1024*1024):.2f} GB")
        return True
    
    return False

def main():
    """
    Main download function
    """
    logger.info("🏁 GR Cup Data Downloader")
    logger.info("=" * 50)
    logger.info("Downloading official Toyota Racing Development hackathon data")
    logger.info("Source: https://trddev.com/hackathon-2025/")
    logger.info("")
    
    # Create directories
    create_directories()
    
    # Download all files
    raw_path = Path("data/raw")
    successful_downloads = 0
    failed_downloads = 0
    
    for track_name, url in DATA_URLS.items():
        filename = f"{track_name}.zip"
        filepath = raw_path / filename
        
        if download_file(url, filepath):
            successful_downloads += 1
        else:
            failed_downloads += 1
    
    # Summary
    logger.info(f"\n📊 Download Summary:")
    logger.info(f"✅ Successful: {successful_downloads}")
    logger.info(f"❌ Failed: {failed_downloads}")
    logger.info(f"📁 Total files: {len(DATA_URLS)}")
    
    if failed_downloads > 0:
        logger.warning(f"\n⚠️  Some downloads failed. You can:")
        logger.info("1. Run this script again to retry failed downloads")
        logger.info("2. Download manually from: https://trddev.com/hackathon-2025/")
        logger.info("3. Check your internet connection")
    
    # Verify downloads
    if successful_downloads > 0:
        verify_downloads()
    
    # Next steps
    if successful_downloads == len(DATA_URLS):
        logger.info(f"\n🚀 Next steps:")
        logger.info("1. Extract and process data:")
        logger.info("   python scripts/process_real_data.py")
        logger.info("2. Train model with real data:")
        logger.info("   python scripts/train_model.py")
        logger.info("3. Test predictions:")
        logger.info("   python demo/race_demo.py")
    
    return successful_downloads == len(DATA_URLS)

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠️  Download cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)