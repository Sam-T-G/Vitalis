#!/bin/bash
# Emergency Relief AI Environment Activation Script
# Run this before using LM Studio or any Python scripts

echo "Activating Emergency Relief AI Environment..."
echo "Location: $(pwd)"
echo ""

# Activate virtual environment
source venv/bin/activate

echo "Virtual environment activated"
echo "Python version: $(python --version)"
echo "PyTorch version: $(python -c 'import torch; print(torch.__version__)')"
echo "MPS (Apple Silicon) available: $(python -c 'import torch; print(torch.backends.mps.is_available())')"
echo ""

echo "Available commands:"
echo "  - LM Studio: Open LM Studio app"
echo "  - Test model: python test_model.py"
echo "  - Fine-tune: Use LM Studio GUI"
echo ""

echo "Ready for Emergency Relief AI training!"
echo "Remember: Keep this terminal open while using LM Studio"
