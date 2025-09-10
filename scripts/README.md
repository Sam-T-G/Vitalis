# Scripts

This directory contains utility scripts and tools for the Vitalis emergency relief AI project.

## Contents

### Environment Management

- **[activate_environment.sh](activate_environment.sh)** - Environment activation script for emergency relief AI development

### Training and Fine-tuning

- **[train_emergency_relief_ai.py](train_emergency_relief_ai.py)** - Main training script for emergency relief AI
- **[train_lora_emergency_relief.py](train_lora_emergency_relief.py)** - LoRA fine-tuning script for emergency relief
- **[validate_training_pipeline.py](validate_training_pipeline.py)** - Training pipeline validation

### Model Testing and Deployment

- **[test_emergency_relief_model.py](test_emergency_relief_model.py)** - Test emergency relief model functionality
- **[test_trained_lora_model.py](test_trained_lora_model.py)** - Test LoRA fine-tuned model (fixed version)
- **[test_trained_lora_model_optimized.py](test_trained_lora_model_optimized.py)** - Optimized testing with better memory management
- **[quick_model_diagnostic.py](quick_model_diagnostic.py)** - Quick model health check and diagnostics
- **[deploy_emergency_relief_api.py](deploy_emergency_relief_api.py)** - API deployment script

### User Testing and Interaction

- **[interactive_emergency_assistant.py](interactive_emergency_assistant.py)** - Interactive chat interface for user testing
- **[test_emergency_scenarios.py](test_emergency_scenarios.py)** - Comprehensive scenario testing with quality scoring
- **[emergency_relief_web_demo.py](emergency_relief_web_demo.py)** - Web interface for user-friendly testing

### Utilities

- **[hello_transformers.py](utilities/hello_transformers.py)** - Basic model loading and testing script
- **[test_emergency_relief_concept.py](test_emergency_relief_concept.py)** - Concept validation testing
- **[lm_studio_training_guide.py](lm_studio_training_guide.py)** - LM Studio integration guide

## Usage

### Environment Setup

```bash
# Activate the development environment
./scripts/activate_environment.sh
```

### Model Testing

```bash
# Quick model health check (recommended first step)
python scripts/quick_model_diagnostic.py

# Test LoRA fine-tuned model (optimized version)
python scripts/test_trained_lora_model_optimized.py

# Test basic model functionality
python scripts/utilities/hello_transformers.py
```

### User Testing (How Users Would Interact)

```bash
# Interactive chat with Emergency Relief AI (recommended for user testing)
python scripts/interactive_emergency_assistant.py

# Comprehensive emergency scenario testing with quality scoring
python scripts/test_emergency_scenarios.py

# Web interface demo (most user-friendly)
python scripts/emergency_relief_web_demo.py
# Then open browser to: http://localhost:5000
```

### Troubleshooting

If you encounter model hanging or generation issues:

1. **Run Quick Diagnostic**: Start with `quick_model_diagnostic.py` to verify basic functionality
2. **Check Troubleshooting Log**: See [model-troubleshooting-log.md](../docs/emergency-relief-ai/model-troubleshooting-log.md) for common issues and solutions
3. **Use Optimized Scripts**: Use `test_trained_lora_model_optimized.py` for better error handling

Common fixes:

- Ensure proper tokenizer configuration (pad_token vs eos_token)
- Use timeout protection for generation calls
- Match dtypes between base model and LoRA adapters
- Clear memory between generation calls

## Environment Requirements

- Python 3.13+
- PyTorch with MPS support
- Transformers library
- Accelerate library
- Virtual environment (venv)

## Related Documentation

- [User Testing Guide](../docs/emergency-relief-ai/USER_TESTING_GUIDE.md) - **Start here** for testing as users would
- [GPT-OSS 20B Setup Guide](../docs/gpt-oss-20b/setup-guide.md) - Detailed setup instructions
- [Emergency Relief AI Implementation](../docs/emergency-relief-ai/) - Implementation guidance
- [Model Troubleshooting Log](../docs/emergency-relief-ai/model-troubleshooting-log.md) - Troubleshooting guide for model issues
- [Model Inference Recommendations](../docs/emergency-relief-ai/model-inference-recommendations.md) - Deployment and optimization guidance
- [Troubleshooting Summary](../docs/emergency-relief-ai/TROUBLESHOOTING_SUMMARY.md) - Quick reference for common issues
