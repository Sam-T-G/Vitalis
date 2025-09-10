# Training Data

This directory contains the training datasets for the emergency relief AI system.

## Contents

### Training Datasets

- **[Emergency Relief Training Data](EMERGENCY_RELIEF_TRAINING_DATA.json)** - Original training dataset with 50 examples across 8 categories
- **[Enhanced Emergency Relief Training Data](ENHANCED_EMERGENCY_RELIEF_TRAINING_DATA.json)** - Enhanced training dataset with 150 examples across 16 categories

## Dataset Information

### Original Dataset

- **Size**: 50 training examples
- **Categories**: 8 emergency relief domains
- **Sources**: FEMA, Red Cross, WHO, UN OCHA, NEMA
- **Format**: LM Studio compatible JSON structure

### Enhanced Dataset

- **Size**: 150 training examples
- **Categories**: 16 emergency relief domains
- **Sources**: 10 authoritative organizations
- **Format**: Enhanced JSON with metadata and standards compliance
- **Standards**: Aligned with FEMA, WHO, Red Cross, Sphere, and ISO standards

## Usage

These datasets are designed for fine-tuning GPT-OSS 20B for emergency relief scenarios using LM Studio or similar fine-tuning platforms.

## Related Documentation

- [Training Data Analysis](../docs/training-data-analysis/) - Comprehensive analysis and enhancement plans
- [Emergency Relief AI](../docs/emergency-relief-ai/) - Implementation guidance and resources
