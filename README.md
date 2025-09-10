# Vitalis

This is the main repository for the Vitalis project - an emergency relief AI system powered by GPT-OSS 20B, fine-tuned for disaster response and emergency management.

## Project Overview

Vitalis is an AI-powered emergency relief system designed to provide expert guidance for disaster response, resource coordination, and emergency management operations. The system leverages GPT-OSS 20B, fine-tuned specifically for emergency relief scenarios using comprehensive training data aligned with international standards.

## Repository Structure

### Core Components

- **[Data](data/)** - Training datasets for emergency relief AI
- **[Scripts](scripts/)** - Utility scripts and environment management
- **[Models](models/)** - GPT-OSS 20B model files and configurations
- **[Documentation](docs/)** - Comprehensive project documentation

### Key Features

- **Emergency Relief AI**: Fine-tuned GPT-OSS 20B for disaster response
- **Standards Compliance**: Aligned with FEMA, WHO, Red Cross, and international protocols
- **M4 MacBook Pro Optimization**: Native Apple Silicon performance
- **PyTorch Training Pipeline**: Comprehensive fine-tuning system with robust error handling

## Quick Start

### For Emergency Relief AI Training

1. **Validate Pipeline**: Run `python scripts/validate_training_pipeline.py`
2. **Start Training**: Execute `python scripts/train_emergency_relief_ai.py`
3. **Test Model**: Validate with `python scripts/test_emergency_relief_model.py`
4. **Deploy API**: Launch `python scripts/deploy_emergency_relief_api.py`

### For Development Setup

1. **Training Guide**: Read [Complete Training Guide](docs/emergency-relief-ai/TRAINING_GUIDE.md)
2. **Review Training Data**: Examine [Enhanced Training Dataset](data/ENHANCED_EMERGENCY_RELIEF_TRAINING_DATA.json)
3. **Implementation Notes**: Study [Emergency Relief AI Implementation](docs/emergency-relief-ai/implementation-notes.md)
4. **Activate Environment**: Run `source venv/bin/activate`

### For Documentation

1. **Main Documentation**: [Documentation Library](docs/README.md)
2. **Training Data Analysis**: [Analysis and Enhancement Plans](docs/training-data-analysis/)
3. **Emergency Relief AI**: [Core AI Documentation](docs/emergency-relief-ai/)
4. **Guidelines**: [Documentation Standards](docs/guidelines/)

## Documentation

### Core Documentation

- **[Documentation Library](docs/README.md)** - Main documentation index and navigation
- **[Emergency Relief AI](docs/emergency-relief-ai/)** - Core AI component documentation
- **[Training Data Analysis](docs/training-data-analysis/)** - Analysis and enhancement plans
- **[GPT-OSS 20B Implementation](docs/gpt-oss-20b/)** - Technical setup and configuration

### Development Resources

- **[Application Development](docs/application-development/)** - General development documentation
- **[Guidelines](docs/guidelines/)** - Documentation standards and coding guidelines
- **[Templates](docs/templates/)** - Reusable documentation templates

## Project Status

### Current Status

- **Training Pipeline**: Complete PyTorch training system ready for execution
- **Model Setup**: GPT-OSS 20B (38.5GB, 4-bit quantized) validated and ready
- **Training Data**: 31 enhanced emergency relief examples across 16 categories
- **Validation**: All 7 pipeline checks passed - ready to train
- **Hardware**: M4 MacBook Pro (48GB RAM) optimally configured

### Training Status

- **LoRA Training**: COMPLETED SUCCESSFULLY (September 10, 2025)
- **Training Duration**: 4 hours 59 seconds
- **Training Loss**: Improved from 4.35 to 3.44 (26% reduction)
- **Validation Loss**: 3.941 (excellent generalization)
- **Parameters Trained**: 1,990,656 out of 20,916,747,840 (0.0095%)
- **Model Saved**: models/emergency_relief_fine_tuned/emergency_relief_lora/

### Recent Updates

- **2025-09-10**: BREAKTHROUGH - LoRA emergency relief training completed successfully
- **2025-09-10**: Resolved dtype alignment issues for Apple Silicon optimization
- **2025-09-10**: Complete PyTorch training pipeline implemented and validated
- **2025-09-10**: All 7 pipeline validation checks passed - ready for training
- **2025-09-10**: M4 MacBook Pro optimization completed (48GB RAM, MPS support)
- **2025-09-10**: Comprehensive training system with error handling and monitoring
- **2025-09-10**: API deployment system and testing framework completed
- **2025-01-09**: Enhanced training dataset created with emergency relief examples
- **2025-01-09**: Model audit completed - GPT-OSS 20B ready for emergency relief training

## Development Setup

### Prerequisites

- **Hardware**: M4 MacBook Pro with 16GB+ unified memory (48GB optimal)
- **Software**: Python 3.13+, PyTorch 2.8.0+, Transformers 4.56.1+
- **Storage**: 100GB+ available space for model and training data
- **Model**: GPT-OSS 20B (4-bit quantized, 38.5GB)

### Getting Started

1. **Validate Setup**: `python scripts/validate_training_pipeline.py`
2. **Activate Environment**: `source venv/bin/activate`
3. **Read Training Guide**: [Complete Training Guide](docs/emergency-relief-ai/TRAINING_GUIDE.md)
4. **Start Training**: `python scripts/train_emergency_relief_ai.py`

## License

This project is licensed under the [LICENSE](LICENSE) file.

---

_This documentation system is designed to grow with the project. Please contribute to its improvement and maintenance._
