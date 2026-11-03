#!/bin/bash
echo "==========================================="
echo "🔧 Label Validator Setup"
echo "==========================================="

VENV_PATH="$HOME/.venvs/label_validator_env"

if [ -d "$VENV_PATH" ]; then
    echo "Virtual environment exists. Updating packages..."
    source "$VENV_PATH/bin/activate"
    pip install --upgrade dash pandas pillow plotly numpy opencv-python
    deactivate
    echo "✅ Setup complete!"
    exit 0
fi

echo "Creating virtual environment at $VENV_PATH..."
python3 -m venv "$VENV_PATH"

source "$VENV_PATH/bin/activate"
pip install --upgrade pip
pip install dash pandas pillow plotly numpy opencv-python

echo ""
echo "Testing imports..."
python << 'EOF'
import os; os.environ['DASH_DISABLE_JUPYTER'] = '1'
import dash; print(f"✓ Dash {dash.__version__}")
import pandas; print(f"✓ Pandas {pandas.__version__}")
import PIL; print(f"✓ Pillow {PIL.__version__}")
import plotly; print(f"✓ Plotly {plotly.__version__}")
try:
    import cv2; print(f"✓ OpenCV {cv2.__version__}")
except: print("⚠ OpenCV not installed")
EOF

deactivate

echo ""
echo "==========================================="
echo "✅ Setup complete!"
echo "Run: sh run_local.sh"
echo "==========================================="
