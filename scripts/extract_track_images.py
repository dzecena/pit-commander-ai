"""
Extract Track Layout Images from PDFs

This script extracts track layout images from the first page of each track PDF
and prepares them for dashboard integration.
"""

import fitz  # PyMuPDF
from pathlib import Path
import json
from PIL import Image
import base64
import io
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrackImageExtractor:
    """
    Extract track layout images from PDF documents
    """
    
    def __init__(self):
        self.pdf_dir = Path("Track Maps")
        self.output_dir = Path("track_images")
        self.output_dir.mkdir(exist_ok=True)
        
        # Map PDF files to track IDs
        self.pdf_mapping = {
            'BMP': 'Barber_Circuit_Map.pdf',
            'COTA': 'COTA_Circuit_Map.pdf', 
            'VIR': 'VIR_map.pdf',
            'SEB': 'Sebring_Track_Sector_Map.pdf',
            'SON': 'Sonoma_Map.pdf',
            'RA': 'Road_America_Map.pdf',
            'INDY': 'Indy_Circuit_Map.pdf'
        }
    
    def extract_first_page_image(self, pdf_path, track_id):
        """
        Extract the first page of PDF as high-quality image
        """
        logger.info(f"🖼️ Extracting track image for {track_id}")
        
        try:
            # Open PDF
            pdf_document = fitz.open(pdf_path)
            
            # Get first page
            first_page = pdf_document[0]
            
            # Convert to image with high resolution
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
            pix = first_page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            # Save as PNG
            output_path = self.output_dir / f"{track_id}_track_layout.png"
            img.save(output_path, "PNG", optimize=True, quality=95)
            
            # Also create a smaller version for web
            img_small = img.copy()
            img_small.thumbnail((800, 600), Image.Resampling.LANCZOS)
            web_path = self.output_dir / f"{track_id}_track_layout_web.png"
            img_small.save(web_path, "PNG", optimize=True, quality=85)
            
            # Convert to base64 for embedding in HTML
            buffer = io.BytesIO()
            img_small.save(buffer, format='PNG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            pdf_document.close()
            
            logger.info(f"✅ Extracted {track_id} track image: {output_path}")
            
            return {
                'track_id': track_id,
                'image_path': str(output_path),
                'web_image_path': str(web_path),
                'base64_data': img_base64,
                'image_size': img.size,
                'web_size': img_small.size
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting {track_id} image: {e}")
            return None
    
    def extract_all_track_images(self):
        """
        Extract track images for all available PDFs
        """
        logger.info("🏁 Extracting Track Layout Images from PDFs")
        logger.info("=" * 50)
        
        extraction_results = {}
        
        for track_id, pdf_filename in self.pdf_mapping.items():
            pdf_path = self.pdf_dir / pdf_filename
            
            if pdf_path.exists():
                result = self.extract_first_page_image(pdf_path, track_id)
                if result:
                    extraction_results[track_id] = result
                else:
                    extraction_results[track_id] = {'status': 'failed'}
            else:
                logger.warning(f"⚠️ PDF not found: {pdf_path}")
                extraction_results[track_id] = {'status': 'missing', 'pdf_path': str(pdf_path)}
        
        # Save extraction results
        results_file = self.output_dir / "track_images_manifest.json"
        with open(results_file, 'w') as f:
            json.dump(extraction_results, f, indent=2)
        
        successful_extractions = [t for t, r in extraction_results.items() if 'image_path' in r]
        
        logger.info(f"\n📊 Track Image Extraction Summary:")
        logger.info(f"✅ Successfully extracted: {len(successful_extractions)} track images")
        logger.info(f"🖼️ Images saved to: {self.output_dir}")
        logger.info(f"📋 Manifest saved: {results_file}")
        
        if successful_extractions:
            logger.info(f"🏎️ Tracks with images: {', '.join(successful_extractions)}")
        
        return extraction_results
    
    def create_dashboard_image_data(self):
        """
        Create JavaScript data structure for dashboard integration
        """
        logger.info("🌐 Creating dashboard image integration data...")
        
        # Load extraction results
        results_file = self.output_dir / "track_images_manifest.json"
        if not results_file.exists():
            logger.error("❌ No extraction results found. Run extract_all_track_images() first.")
            return None
        
        with open(results_file, 'r') as f:
            extraction_results = json.load(f)
        
        # Create JavaScript object for dashboard
        dashboard_images = {}
        
        for track_id, result in extraction_results.items():
            if 'base64_data' in result:
                dashboard_images[track_id] = {
                    'image_data': f"data:image/png;base64,{result['base64_data']}",
                    'width': result['web_size'][0],
                    'height': result['web_size'][1],
                    'alt_text': f"{track_id} Track Layout"
                }
        
        # Save as JavaScript file
        js_file = self.output_dir / "track_images.js"
        js_content = f"const TRACK_IMAGES = {json.dumps(dashboard_images, indent=2)};"
        
        with open(js_file, 'w') as f:
            f.write(js_content)
        
        logger.info(f"✅ Dashboard image data created: {js_file}")
        logger.info(f"🖼️ {len(dashboard_images)} track images ready for dashboard")
        
        return dashboard_images

def main():
    """
    Main function to extract all track images
    """
    print("🏁 GR Cup Track Image Extractor")
    print("=" * 40)
    print("Extracting track layout images from PDF documents")
    print("for dashboard integration...")
    print()
    
    extractor = TrackImageExtractor()
    
    # Extract all images
    results = extractor.extract_all_track_images()
    
    # Create dashboard integration data
    dashboard_data = extractor.create_dashboard_image_data()
    
    if dashboard_data:
        print("\n🎯 Next Steps:")
        print("1. Upload track images to S3:")
        print("   aws s3 sync track_images/ s3://gr-cup-data-dev-us-east-1-v2/track-images/")
        print("2. Update dashboard to display track images")
        print("3. Images will refresh when track selection changes")
        print()
        print("✅ Track images ready for dashboard integration!")
    else:
        print("❌ Image extraction failed. Check the logs above.")

if __name__ == "__main__":
    main()