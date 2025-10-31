"""
Simple PDF text extraction for GR Cup data

Author: GR Cup Analytics Team
Date: 2025-10-30

This script provides a basic PDF text extraction approach
that works without complex dependencies.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import sys
import re
from typing import List, Dict, Any, Optional

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from utils.config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def find_pdf_files() -> List[Path]:
    """
    Find all PDF files in the project directories
    """
    pdf_files = []
    
    # Check multiple directories
    search_dirs = [
        Path("data/raw"),
        Path("Track Maps"), 
        Path("Data Files"),
        Path(".")  # Current directory
    ]
    
    for search_dir in search_dirs:
        if search_dir.exists():
            found_pdfs = list(search_dir.glob("*.pdf"))
            pdf_files.extend(found_pdfs)
            if found_pdfs:
                logger.info(f"Found {len(found_pdfs)} PDFs in {search_dir}")
    
    return pdf_files

def analyze_pdf_content(pdf_path: Path) -> Dict[str, Any]:
    """
    Analyze PDF content without complex libraries
    """
    logger.info(f"Analyzing: {pdf_path.name}")
    
    analysis = {
        'filename': pdf_path.name,
        'size_mb': pdf_path.stat().st_size / (1024 * 1024),
        'likely_content': 'unknown',
        'recommendations': []
    }
    
    # Analyze filename for clues
    filename_lower = pdf_path.name.lower()
    
    if any(word in filename_lower for word in ['telemetry', 'data', 'sensor', 'acquisition']):
        analysis['likely_content'] = 'telemetry_data'
        analysis['recommendations'].append("Likely contains telemetry data - look for speed, RPM, throttle columns")
    
    elif any(word in filename_lower for word in ['lap', 'timing', 'sector', 'split']):
        analysis['likely_content'] = 'lap_times'
        analysis['recommendations'].append("Likely contains lap times - look for lap numbers and time columns")
    
    elif any(word in filename_lower for word in ['result', 'classification', 'final', 'position']):
        analysis['likely_content'] = 'race_results'
        analysis['recommendations'].append("Likely contains race results - look for position and driver columns")
    
    elif any(word in filename_lower for word in ['analysis', 'report', 'summary']):
        analysis['likely_content'] = 'analysis_report'
        analysis['recommendations'].append("Likely contains analysis data - may have multiple data types")
    
    # Track identification
    track_indicators = {
        'barber': 'Barber Motorsports Park',
        'cota': 'Circuit of the Americas',
        'indianapolis': 'Indianapolis Motor Speedway',
        'indy': 'Indianapolis Motor Speedway',
        'road-america': 'Road America',
        'sebring': 'Sebring International Raceway',
        'sonoma': 'Sonoma Raceway',
        'vir': 'Virginia International Raceway',
        'virginia': 'Virginia International Raceway'
    }
    
    for indicator, track_name in track_indicators.items():
        if indicator in filename_lower:
            analysis['track'] = track_name
            analysis['recommendations'].append(f"Associated with {track_name}")
            break
    
    return analysis

def extract_text_simple(pdf_path: Path) -> str:
    """
    Simple text extraction using basic methods
    """
    try:
        # Try using PyPDF2 if available
        try:
            import PyPDF2
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                
                return text
        
        except ImportError:
            logger.warning("PyPDF2 not available, trying alternative method")
            return ""
    
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path}: {e}")
        return ""

def find_tabular_data_in_text(text: str) -> List[Dict[str, Any]]:
    """
    Find potential tabular data in extracted text
    """
    if not text:
        return []
    
    tables = []
    lines = text.split('\n')
    
    # Look for lines that might be table headers or data
    potential_table_lines = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Look for lines with multiple numeric values (potential data rows)
        numbers = re.findall(r'\d+\.?\d*', line)
        if len(numbers) >= 3:  # At least 3 numbers suggests tabular data
            potential_table_lines.append({
                'line_number': i,
                'content': line,
                'numbers_found': len(numbers),
                'numbers': numbers
            })
    
    # Group consecutive lines that might form tables
    if potential_table_lines:
        tables.append({
            'type': 'numeric_data',
            'lines': potential_table_lines,
            'description': f"Found {len(potential_table_lines)} lines with numeric data"
        })
    
    # Look for common racing data patterns
    racing_patterns = {
        'lap_times': r'lap\s*\d+.*\d+:\d+\.\d+',
        'speeds': r'speed.*\d+.*mph|kmh',
        'sectors': r'sector.*\d+.*\d+\.\d+',
        'positions': r'p\d+|position\s*\d+'
    }
    
    for pattern_name, pattern in racing_patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            tables.append({
                'type': pattern_name,
                'matches': matches[:10],  # First 10 matches
                'description': f"Found {len(matches)} {pattern_name} patterns"
            })
    
    return tables

def generate_extraction_guide(pdf_files: List[Path]) -> None:
    """
    Generate a guide for manual data extraction
    """
    logger.info("\n📋 PDF EXTRACTION GUIDE")
    logger.info("=" * 50)
    
    if not pdf_files:
        logger.warning("No PDF files found!")
        logger.info("\nPlease place your PDF files in one of these directories:")
        logger.info("  📁 data/raw/")
        logger.info("  📁 Track Maps/")
        logger.info("  📁 Data Files/")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process:")
    
    for pdf_file in pdf_files:
        analysis = analyze_pdf_content(pdf_file)
        
        logger.info(f"\n📄 {analysis['filename']}")
        logger.info(f"   Size: {analysis['size_mb']:.1f} MB")
        logger.info(f"   Likely content: {analysis['likely_content']}")
        
        if 'track' in analysis:
            logger.info(f"   Track: {analysis['track']}")
        
        for rec in analysis['recommendations']:
            logger.info(f"   💡 {rec}")
        
        # Try to extract some text
        text_sample = extract_text_simple(pdf_file)
        if text_sample:
            # Find potential tables
            tables = find_tabular_data_in_text(text_sample)
            
            if tables:
                logger.info(f"   📊 Found {len(tables)} potential data sections:")
                for table in tables:
                    logger.info(f"      - {table['description']}")
            
            # Show a small text sample
            sample = text_sample[:300].replace('\n', ' ')
            logger.info(f"   📝 Text sample: {sample}...")
        
        else:
            logger.info("   ❌ Could not extract text (may need manual processing)")
    
    # Generate recommendations
    logger.info(f"\n🎯 NEXT STEPS:")
    logger.info("1. Install PDF processing libraries:")
    logger.info("   pip install PyPDF2 pdfplumber tabula-py")
    
    logger.info("\n2. For each PDF file:")
    logger.info("   a) Open the PDF manually")
    logger.info("   b) Look for tables with columns like:")
    logger.info("      - Telemetry: Time, Speed, RPM, Throttle, Brake, Steering")
    logger.info("      - Lap Times: Lap, Time, Sector1, Sector2, Sector3")
    logger.info("      - Results: Position, Driver, Car, Time, Points")
    
    logger.info("\n3. Export data as CSV:")
    logger.info("   - Copy table data from PDF")
    logger.info("   - Paste into Excel/Google Sheets")
    logger.info("   - Save as CSV in data/extracted/[track-name]/")
    
    logger.info("\n4. Use our naming convention:")
    logger.info("   - [TRACK]_telemetry.csv")
    logger.info("   - [TRACK]_lap_times.csv")
    logger.info("   - [TRACK]_AnalysisEnduranceWithSections.csv")
    logger.info("   - [TRACK]_results.csv")
    
    # Create template directories
    logger.info("\n📁 Creating template directories...")
    
    tracks = ['barber-motorsports-park', 'circuit-of-the-americas', 'indianapolis', 
              'road-america', 'sebring', 'sonoma', 'virginia-international-raceway']
    
    for track in tracks:
        track_dir = Path(f"data/extracted/{track}")
        track_dir.mkdir(parents=True, exist_ok=True)
        
        # Create template files
        template_path = track_dir / "README.txt"
        with open(template_path, 'w') as f:
            f.write(f"Place {track} data files here:\n")
            f.write(f"- {track.upper()}_telemetry.csv\n")
            f.write(f"- {track.upper()}_lap_times.csv\n")
            f.write(f"- {track.upper()}_AnalysisEnduranceWithSections.csv\n")
            f.write(f"- {track.upper()}_results.csv\n")
    
    logger.info("✅ Template directories created in data/extracted/")

def main():
    """
    Main function for PDF analysis
    """
    logger.info("🏁 GR Cup PDF Data Analysis")
    logger.info("=" * 40)
    
    # Find PDF files
    pdf_files = find_pdf_files()
    
    # Generate extraction guide
    generate_extraction_guide(pdf_files)
    
    logger.info(f"\n✅ Analysis complete!")
    
    if pdf_files:
        logger.info(f"\n🚀 Once you have CSV files extracted:")
        logger.info("1. Run: python scripts/process_real_data.py")
        logger.info("2. Run: python scripts/train_model.py")
        logger.info("3. Run: python demo/race_demo.py")

if __name__ == "__main__":
    main()