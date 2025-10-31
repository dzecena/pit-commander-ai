"""
Extract telemetry and race data from PDF files

Author: GR Cup Analytics Team
Date: 2025-10-30

This script extracts data from PDF files containing:
- Telemetry data tables
- Lap time sheets
- Sector analysis
- Race results
- Timing data

Common PDF formats in racing:
- Data acquisition reports
- Timing and scoring sheets
- Session summaries
- Analysis reports
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import sys
import re
from typing import List, Dict, Any, Optional

# PDF processing libraries
try:
    import PyPDF2
    import pdfplumber
    import tabula
    PDF_LIBS_AVAILABLE = True
except ImportError:
    PDF_LIBS_AVAILABLE = False
    print("PDF libraries not installed. Installing...")

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from utils.config import TRACKS, setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def install_pdf_dependencies():
    """
    Install required PDF processing libraries
    """
    import subprocess
    import sys
    
    libraries = [
        'PyPDF2',
        'pdfplumber', 
        'tabula-py',
        'camelot-py[cv]'  # For complex table extraction
    ]
    
    logger.info("Installing PDF processing libraries...")
    
    for lib in libraries:
        try:
            logger.info(f"Installing {lib}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', lib])
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to install {lib}: {e}")
    
    logger.info("PDF libraries installation complete!")

class PDFDataExtractor:
    """
    Extract racing data from PDF files
    """
    
    def __init__(self):
        self.supported_formats = [
            'telemetry_data',
            'lap_times', 
            'sector_analysis',
            'race_results',
            'timing_sheets'
        ]
    
    def analyze_pdf_structure(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Analyze PDF structure to understand content type
        """
        logger.info(f"Analyzing PDF structure: {pdf_path.name}")
        
        analysis = {
            'pages': 0,
            'tables_found': 0,
            'content_type': 'unknown',
            'potential_data': [],
            'text_sample': ''
        }
        
        try:
            # Method 1: Use pdfplumber for detailed analysis
            import pdfplumber
            
            with pdfplumber.open(pdf_path) as pdf:
                analysis['pages'] = len(pdf.pages)
                
                # Analyze first few pages
                for i, page in enumerate(pdf.pages[:3]):
                    text = page.extract_text()
                    if text:
                        analysis['text_sample'] += text[:500] + "\n"
                    
                    # Look for tables
                    tables = page.extract_tables()
                    if tables:
                        analysis['tables_found'] += len(tables)
                        
                        # Analyze table structure
                        for table in tables:
                            if len(table) > 1:  # Has header + data
                                headers = [str(cell).lower() if cell else '' for cell in table[0]]
                                analysis['potential_data'].append({
                                    'page': i + 1,
                                    'headers': headers,
                                    'rows': len(table) - 1
                                })
            
            # Determine content type based on text analysis
            text_lower = analysis['text_sample'].lower()
            
            if any(word in text_lower for word in ['telemetry', 'sensor', 'speed', 'rpm', 'throttle']):
                analysis['content_type'] = 'telemetry_data'
            elif any(word in text_lower for word in ['lap time', 'sector', 'split']):
                analysis['content_type'] = 'lap_times'
            elif any(word in text_lower for word in ['position', 'result', 'classification']):
                analysis['content_type'] = 'race_results'
            elif any(word in text_lower for word in ['analysis', 'endurance', 'session']):
                analysis['content_type'] = 'sector_analysis'
            
        except Exception as e:
            logger.error(f"Error analyzing PDF {pdf_path}: {e}")
        
        return analysis
    
    def extract_tables_pdfplumber(self, pdf_path: Path) -> List[pd.DataFrame]:
        """
        Extract tables using pdfplumber (good for simple tables)
        """
        logger.info(f"Extracting tables with pdfplumber: {pdf_path.name}")
        
        dataframes = []
        
        try:
            import pdfplumber
            
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    tables = page.extract_tables()
                    
                    for table_num, table in enumerate(tables):
                        if len(table) > 1:  # Must have header + data
                            try:
                                # Convert to DataFrame
                                df = pd.DataFrame(table[1:], columns=table[0])
                                
                                # Clean up the DataFrame
                                df = self._clean_extracted_dataframe(df)
                                
                                if not df.empty:
                                    df['source_page'] = page_num + 1
                                    df['source_table'] = table_num + 1
                                    dataframes.append(df)
                                    
                                    logger.info(f"  Extracted table: {df.shape} from page {page_num + 1}")
                            
                            except Exception as e:
                                logger.warning(f"Error processing table on page {page_num + 1}: {e}")
        
        except Exception as e:
            logger.error(f"Error with pdfplumber extraction: {e}")
        
        return dataframes
    
    def extract_tables_tabula(self, pdf_path: Path) -> List[pd.DataFrame]:
        """
        Extract tables using tabula-py (good for complex tables)
        """
        logger.info(f"Extracting tables with tabula: {pdf_path.name}")
        
        dataframes = []
        
        try:
            import tabula
            
            # Extract all tables from all pages
            tables = tabula.read_pdf(str(pdf_path), pages='all', multiple_tables=True)
            
            for i, df in enumerate(tables):
                if not df.empty:
                    # Clean up the DataFrame
                    df = self._clean_extracted_dataframe(df)
                    
                    if not df.empty:
                        df['source_table'] = i + 1
                        dataframes.append(df)
                        
                        logger.info(f"  Extracted table {i + 1}: {df.shape}")
        
        except Exception as e:
            logger.error(f"Error with tabula extraction: {e}")
        
        return dataframes
    
    def extract_tables_camelot(self, pdf_path: Path) -> List[pd.DataFrame]:
        """
        Extract tables using camelot (best for complex layouts)
        """
        logger.info(f"Extracting tables with camelot: {pdf_path.name}")
        
        dataframes = []
        
        try:
            import camelot
            
            # Try lattice method first (for tables with borders)
            try:
                tables = camelot.read_pdf(str(pdf_path), pages='all', flavor='lattice')
                
                for table in tables:
                    df = table.df
                    if not df.empty:
                        df = self._clean_extracted_dataframe(df)
                        if not df.empty:
                            dataframes.append(df)
                            logger.info(f"  Extracted lattice table: {df.shape}")
            
            except Exception as e:
                logger.warning(f"Lattice method failed: {e}")
            
            # Try stream method (for tables without borders)
            if not dataframes:
                try:
                    tables = camelot.read_pdf(str(pdf_path), pages='all', flavor='stream')
                    
                    for table in tables:
                        df = table.df
                        if not df.empty:
                            df = self._clean_extracted_dataframe(df)
                            if not df.empty:
                                dataframes.append(df)
                                logger.info(f"  Extracted stream table: {df.shape}")
                
                except Exception as e:
                    logger.warning(f"Stream method failed: {e}")
        
        except Exception as e:
            logger.error(f"Error with camelot extraction: {e}")
        
        return dataframes
    
    def _clean_extracted_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean up extracted DataFrame
        """
        if df.empty:
            return df
        
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Clean column names
        if not df.empty:
            df.columns = [str(col).strip().replace('\n', ' ').replace('\r', '') for col in df.columns]
            
            # Remove rows that are likely headers repeated in the middle
            if len(df) > 1:
                first_row = df.iloc[0].astype(str).str.lower()
                header_like = df.apply(lambda row: 
                    sum(str(val).lower() in first_row.values for val in row) > len(df.columns) * 0.5, 
                    axis=1)
                df = df[~header_like]
        
        return df
    
    def identify_data_type(self, df: pd.DataFrame, filename: str) -> str:
        """
        Identify what type of racing data this DataFrame contains
        """
        if df.empty:
            return 'unknown'
        
        # Convert columns to lowercase for analysis
        columns_lower = [str(col).lower() for col in df.columns]
        filename_lower = filename.lower()
        
        # Check for telemetry data
        telemetry_indicators = ['speed', 'rpm', 'throttle', 'brake', 'steering', 'gear', 'time', 'distance']
        if sum(any(indicator in col for indicator in telemetry_indicators) for col in columns_lower) >= 3:
            return 'telemetry'
        
        # Check for lap times
        lap_indicators = ['lap', 'time', 'sector', 'split']
        if sum(any(indicator in col for indicator in lap_indicators) for col in columns_lower) >= 2:
            return 'lap_times'
        
        # Check for results
        result_indicators = ['position', 'pos', 'driver', 'car', 'points', 'result']
        if sum(any(indicator in col for indicator in result_indicators) for col in columns_lower) >= 2:
            return 'results'
        
        # Check filename for clues
        if any(word in filename_lower for word in ['telemetry', 'data', 'sensor']):
            return 'telemetry'
        elif any(word in filename_lower for word in ['lap', 'timing', 'sector']):
            return 'lap_times'
        elif any(word in filename_lower for word in ['result', 'classification', 'final']):
            return 'results'
        
        return 'unknown'
    
    def convert_to_standard_format(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """
        Convert extracted data to our standard format
        """
        if df.empty:
            return df
        
        logger.info(f"Converting {data_type} data to standard format")
        
        if data_type == 'telemetry':
            return self._standardize_telemetry(df)
        elif data_type == 'lap_times':
            return self._standardize_lap_times(df)
        elif data_type == 'results':
            return self._standardize_results(df)
        else:
            return df
    
    def _standardize_telemetry(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize telemetry data format
        """
        # Map common column variations to standard names
        column_mapping = {
            'speed': ['speed', 'velocity', 'spd', 'v'],
            'rpm': ['rpm', 'engine_rpm', 'motor_rpm', 'nmotor'],
            'throttle': ['throttle', 'ath', 'accelerator', 'gas'],
            'brake': ['brake', 'brake_pressure', 'pbrake_f', 'brk'],
            'steering': ['steering', 'steering_angle', 'steer'],
            'gear': ['gear', 'transmission'],
            'time': ['time', 'timestamp', 'elapsed_time'],
            'lap': ['lap', 'lap_number', 'lap_count'],
            'distance': ['distance', 'track_distance', 'dist']
        }
        
        standardized_df = df.copy()
        
        # Apply column mapping
        for standard_name, variations in column_mapping.items():
            for col in df.columns:
                if any(var in str(col).lower() for var in variations):
                    if standard_name not in standardized_df.columns:
                        standardized_df[standard_name] = df[col]
                    break
        
        # Convert numeric columns
        numeric_columns = ['speed', 'rpm', 'throttle', 'brake', 'steering', 'gear', 'time', 'lap', 'distance']
        for col in numeric_columns:
            if col in standardized_df.columns:
                standardized_df[col] = pd.to_numeric(standardized_df[col], errors='coerce')
        
        return standardized_df
    
    def _standardize_lap_times(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize lap time data format
        """
        # Common lap time formats: MM:SS.sss, SS.sss, etc.
        def parse_lap_time(time_str):
            if pd.isna(time_str):
                return np.nan
            
            time_str = str(time_str).strip()
            
            # Format: MM:SS.sss
            if ':' in time_str:
                try:
                    parts = time_str.split(':')
                    minutes = float(parts[0])
                    seconds = float(parts[1])
                    return minutes * 60 + seconds
                except:
                    return np.nan
            
            # Format: SS.sss
            try:
                return float(time_str)
            except:
                return np.nan
        
        standardized_df = df.copy()
        
        # Find time columns and convert them
        for col in df.columns:
            if any(word in str(col).lower() for word in ['time', 'sector', 'split']):
                if df[col].dtype == 'object':  # String column, likely time format
                    standardized_df[col] = df[col].apply(parse_lap_time)
        
        return standardized_df
    
    def _standardize_results(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize race results format
        """
        # Standard results should have: position, driver, car, time, etc.
        return df  # Basic implementation for now

def process_pdf_files():
    """
    Main function to process all PDF files
    """
    logger.info("🏁 Processing PDF Files for GR Cup Data")
    logger.info("=" * 50)
    
    # Check if PDF libraries are available
    if not PDF_LIBS_AVAILABLE:
        install_pdf_dependencies()
        
        # Try importing again
        try:
            import PyPDF2
            import pdfplumber
            import tabula
            logger.info("✅ PDF libraries successfully installed")
        except ImportError:
            logger.error("❌ Failed to install PDF libraries")
            logger.info("Please install manually:")
            logger.info("pip install PyPDF2 pdfplumber tabula-py camelot-py[cv]")
            return False
    
    extractor = PDFDataExtractor()
    
    # Find PDF files in data directories
    pdf_files = []
    
    # Check data/raw for PDFs
    raw_path = Path("data/raw")
    if raw_path.exists():
        pdf_files.extend(raw_path.glob("*.pdf"))
    
    # Check Track Maps for PDFs
    track_maps_path = Path("Track Maps")
    if track_maps_path.exists():
        pdf_files.extend(track_maps_path.glob("*.pdf"))
    
    # Check Data Files for PDFs
    data_files_path = Path("Data Files")
    if data_files_path.exists():
        pdf_files.extend(data_files_path.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning("No PDF files found!")
        logger.info("Please place PDF files in one of these directories:")
        logger.info("  - data/raw/")
        logger.info("  - Track Maps/")
        logger.info("  - Data Files/")
        return False
    
    logger.info(f"Found {len(pdf_files)} PDF files")
    
    # Process each PDF
    all_extracted_data = {}
    
    for pdf_file in pdf_files:
        logger.info(f"\n📄 Processing: {pdf_file.name}")
        
        # Analyze PDF structure
        analysis = extractor.analyze_pdf_structure(pdf_file)
        logger.info(f"  Pages: {analysis['pages']}, Tables: {analysis['tables_found']}")
        logger.info(f"  Content type: {analysis['content_type']}")
        
        # Extract tables using multiple methods
        extracted_tables = []
        
        # Try pdfplumber first (fastest)
        tables_pdfplumber = extractor.extract_tables_pdfplumber(pdf_file)
        extracted_tables.extend(tables_pdfplumber)
        
        # If no tables found, try tabula
        if not extracted_tables:
            tables_tabula = extractor.extract_tables_tabula(pdf_file)
            extracted_tables.extend(tables_tabula)
        
        # If still no tables, try camelot
        if not extracted_tables:
            tables_camelot = extractor.extract_tables_camelot(pdf_file)
            extracted_tables.extend(tables_camelot)
        
        # Process extracted tables
        if extracted_tables:
            logger.info(f"  ✅ Extracted {len(extracted_tables)} tables")
            
            for i, df in enumerate(extracted_tables):
                # Identify data type
                data_type = extractor.identify_data_type(df, pdf_file.name)
                logger.info(f"    Table {i+1}: {data_type} ({df.shape})")
                
                # Convert to standard format
                standardized_df = extractor.convert_to_standard_format(df, data_type)
                
                # Save extracted data
                output_dir = Path("data/extracted_from_pdf")
                output_dir.mkdir(exist_ok=True)
                
                output_filename = f"{pdf_file.stem}_table_{i+1}_{data_type}.csv"
                output_path = output_dir / output_filename
                
                standardized_df.to_csv(output_path, index=False)
                logger.info(f"    💾 Saved to: {output_path}")
                
                # Store in memory for analysis
                if pdf_file.stem not in all_extracted_data:
                    all_extracted_data[pdf_file.stem] = []
                all_extracted_data[pdf_file.stem].append({
                    'data_type': data_type,
                    'dataframe': standardized_df,
                    'filename': output_filename
                })
        
        else:
            logger.warning(f"  ❌ No tables extracted from {pdf_file.name}")
    
    # Generate summary report
    logger.info(f"\n📊 EXTRACTION SUMMARY:")
    logger.info(f"  PDFs processed: {len(pdf_files)}")
    logger.info(f"  Files with data: {len(all_extracted_data)}")
    
    total_tables = sum(len(data) for data in all_extracted_data.values())
    logger.info(f"  Total tables extracted: {total_tables}")
    
    # Count by data type
    data_type_counts = {}
    for file_data in all_extracted_data.values():
        for table_data in file_data:
            data_type = table_data['data_type']
            data_type_counts[data_type] = data_type_counts.get(data_type, 0) + 1
    
    logger.info("  Data types found:")
    for data_type, count in data_type_counts.items():
        logger.info(f"    {data_type}: {count} tables")
    
    logger.info(f"\n✅ PDF extraction complete!")
    logger.info(f"📁 Extracted data saved to: data/extracted_from_pdf/")
    
    return True

if __name__ == "__main__":
    process_pdf_files()