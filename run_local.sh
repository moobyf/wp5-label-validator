#!/bin/bash
# run_local.sh - Run Label Validator locally

echo "==========================================="
echo "🔍 Label Validator - Local Mode"
echo "==========================================="

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check for virtual environment
if [ -d "venv" ]; then
    echo "Using local venv..."
    source venv/bin/activate
elif [ -d "$HOME/.venvs/label_validator_env" ]; then
    echo "Using home venv..."
    source "$HOME/.venvs/label_validator_env/bin/activate"
fi

# Check dependencies
python -c "import dash, pandas, PIL, plotly" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Missing dependencies. Installing..."
    pip install dash pandas pillow plotly numpy opencv-python
fi

export DASH_DISABLE_JUPYTER=1

PORT=${1:-8050}

python index.py --port $PORT --host 127.0.0.1
