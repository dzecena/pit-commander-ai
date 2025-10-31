# CSV Templates for GR Cup Data

These templates show the exact format needed for your extracted PDF data.

## Files:

### Core Templates:
- `telemetry_template.csv` - Main telemetry data format
- `lap_times_template.csv` - Lap timing data format  
- `sector_analysis_template.csv` - 6-sector timing format
- `results_template.csv` - Race results format

### Track Examples:
- `virginia-international-raceway/` - VIR examples
- `sebring/` - Sebring examples
- `circuit-of-the-americas/` - COTA examples

## Usage:

1. Extract data from your PDFs
2. Format it to match these templates
3. Save with proper naming: `[TRACK]_[type].csv`
4. Place in `data/extracted/[track-folder]/`

## Key Points:

- **Column names must match exactly**
- **Numeric data should be numbers, not text**
- **Times can be in seconds (105.234) or MM:SS.sss format**
- **Vehicle IDs should follow GR86-chassis-carnum format**
- **Timestamps in milliseconds since epoch**

## Next Steps:

After creating your CSV files:
```bash
python scripts/process_real_data.py
python scripts/train_model.py
python demo/race_demo.py
```
