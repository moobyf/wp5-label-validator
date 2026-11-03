# 🔍 Interactive Label Validator

Application for validating ML model predictions on fish species images.

## Features

- Browse and validate image predictions from YOLO and DINO models
- View full video frames with all detected bboxes
- Edit bounding boxes and add new detections
- Filter by validation status and species
- Thumbnail gallery for quick navigation
- Session persistence (resume where you left off)
- CSV export with validation source tracking (YOLO/DINO/manual)
- Auto-organize images into label folders

## Quick Start - Local Computer

### Linux/Mac
```bash
unzip label_validator.zip
cd label_validator
./run_local.sh
```

### Windows
```
1. Unzip label_validator.zip
2. Double-click run_local.bat
```

The browser will open automatically at http://localhost:8050

## Installation Options

### Option 1: Quick Run (if you have Python 3.8+)

```bash
cd label_validator
pip install dash pandas pillow plotly numpy opencv-python
python index.py
# Open http://localhost:8050
```

### Option 2: With Virtual Environment (recommended)

**Linux/Mac:**
```bash
cd label_validator
python3 -m venv venv
source venv/bin/activate
pip install dash pandas pillow plotly numpy opencv-python
python index.py
```

**Windows:**
```cmd
cd label_validator
python -m venv venv
venv\Scripts\activate
pip install dash pandas pillow plotly numpy opencv-python
python index.py
```

### Option 3: SLURM Cluster (JupyterHub)

```bash
# 1. Copy to your workspace
cp -r label_validator ~/Dash/

# 2. Setup virtual environment (one time)
cd ~/Dash/label_validator
bash setup.sh

# 3. Run
cd ~/Dash
sbatch label_validator/run_validator.sh

# 4. Access via JupyterHub proxy (URL in dash_validator.log)
```

## Usage

1. **Select CSV file**: Your predictions CSV with columns like `image_path`, `YOLO_Prediction`, `DINO_Prediction`, etc.

2. **Select Images Directory**: Root folder containing the crop images

3. **Select Output Directory** (optional): Where to save the validated CSV

4. **Select Videos Directory** (optional): For viewing full frames

5. **Start Validation**: Click the button to begin

### Validation Workflow

- Click **YOLO** or **DINO** prediction buttons to use that label
- Or select from the label list
- Or add a new custom label
- Click **SAVE & NEXT** to validate and move to next image
- Images are automatically moved to their label folder

### Species Filter with Thumbnails

When you filter by species, a thumbnail gallery appears showing all images for that species. Click any thumbnail to jump directly to that image.

### CSV Output

The validated CSV includes:
- `validated`: 'Yes' or 'No'
- `final_label`: The validated label
- `validation_source`: 'YOLO', 'DINO', or 'manual'
- `image_path`: Updated path (if image was moved)

## File Structure

```
label_validator/
├── index.py              # Main entry point
├── run_local.sh          # Local run script (Linux/Mac)
├── run_local.bat         # Local run script (Windows)
├── run_validator.sh      # SLURM launch script
├── setup.sh              # Virtual environment setup
├── requirements.txt      # Python dependencies
├── app.py                # Dash app initialization
├── config.py             # Configuration
├── assets/
│   └── style.css
├── callbacks/            # All callback functions
├── components/           # Reusable UI components
├── layouts/              # Page layouts
└── utils/                # Utility functions
```

## Troubleshooting

### "Module not found" errors
```bash
pip install dash pandas pillow plotly numpy opencv-python
```

### Port already in use
```bash
python index.py --port 8051
```

### Windows: Script doesn't run
Right-click `run_local.bat` → Run as administrator

### Mac: Permission denied
```bash
chmod +x run_local.sh
./run_local.sh
```

## Requirements

- Python 3.8+
- dash >= 2.14.0
- pandas >= 1.5.0
- Pillow >= 9.0.0
- plotly >= 5.15.0
- numpy >= 1.21.0
- opencv-python >= 4.5.0 (optional, for video frame extraction)
