# Utility Scripts

This directory contains utility scripts for testing and development of the emergency relief AI system.

## Contents

### Model Testing

- **[hello_transformers.py](hello_transformers.py)** - Basic model loading and inference testing script

## Script Descriptions

### hello_transformers.py

- **Purpose**: Test basic GPT-OSS 20B model loading and inference
- **Features**:
  - Model loading with local files
  - Basic inference with emergency relief prompt
  - Text streaming output
- **Usage**: Run from project root directory
- **Requirements**: Activated virtual environment with required dependencies

## Usage

```bash
# From project root directory
python scripts/utilities/hello_transformers.py
```

## Related Documentation

- [GPT-OSS 20B Setup Guide](../../docs/gpt-oss-20b/setup-guide.md)
- [Emergency Relief AI Implementation](../../docs/emergency-relief-ai/)
