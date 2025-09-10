# Emergency Relief AI Training Guide

## Overview

This guide walks you through fine-tuning GPT-OSS 20B for emergency relief scenarios using a comprehensive PyTorch-based pipeline optimized for M4 MacBook Pro.

## Prerequisites Verified COMPLETED

- **Hardware**: M4 MacBook Pro with 48GB RAM (excellent for training)
- **Model**: GPT-OSS 20B (38.5GB, 4-bit quantized)
- **Environment**: Python 3.13 + PyTorch 2.8.0 + Transformers 4.56.1
- **Training Data**: 31 enhanced emergency relief examples across 16 categories
- **Storage**: 98GB free space available

## Training Pipeline Components

### 1. Core Training Script

- **File**: `src/vitalis/training/emergency_relief_trainer.py`
- **Features**: Robust error handling, memory monitoring, multiple loading strategies
- **Optimization**: Apple Silicon MPS support with CPU fallback

### 2. Training Launcher

- **File**: `scripts/train_emergency_relief_ai.py`
- **Purpose**: Interactive training launcher with prerequisites checking
- **Features**: Time estimation, confirmation prompts, progress monitoring

### 3. Model Validation

- **File**: `scripts/test_emergency_relief_model.py`
- **Purpose**: Comprehensive testing across emergency scenarios
- **Output**: Performance metrics and quality assessment

### 4. API Deployment

- **File**: `scripts/deploy_emergency_relief_api.py`
- **Purpose**: Flask API for serving the trained model
- **Features**: REST endpoints, health checks, emergency guidance generation

### 5. Pipeline Validation

- **File**: `scripts/validate_training_pipeline.py`
- **Purpose**: Pre-training validation of all components
- **Status**: All 7 checks passed COMPLETED

## Training Configuration

### Optimized Parameters (M4 MacBook Pro)

```json
{
	"num_epochs": 3,
	"batch_size": 1,
	"gradient_accumulation_steps": 4,
	"learning_rate": 5e-5,
	"max_length": 1024,
	"optimization": "Apple Silicon MPS + memory monitoring"
}
```

### Expected Performance

- **Training Time**: 1-3 hours
- **Memory Usage**: 12-16GB unified memory
- **Model Output**: Emergency relief specialized GPT-OSS 20B
- **Response Time**: 2-5 seconds per query

## Quick Start Instructions

### 1. Start Training (Ready to Execute)

```bash
cd /Users/sam/Documents/repositories/Vitalis
source venv/bin/activate
python scripts/train_emergency_relief_ai.py
```

### 2. Monitor Progress

- Training logs will show memory usage, loss, and progress
- Automatic checkpointing every 100 steps
- Memory monitoring prevents system overload

### 3. Test Trained Model

```bash
python scripts/test_emergency_relief_model.py
```

### 4. Deploy API

```bash
python scripts/deploy_emergency_relief_api.py
```

## Training Data Details

### Enhanced Dataset Specifications

- **Total Examples**: 31 emergency relief scenarios
- **Categories**: 16 specialized domains
- **Format**: Conversation-based with system prompts
- **Quality**: Professional emergency management standards

### Example Categories

1. Disaster Response
2. Shelter Management
3. Resource Coordination
4. Volunteer Management
5. Medical Emergency
6. Communication Protocols
7. Search & Rescue
8. Infrastructure Assessment
9. Public Health
10. Crisis Leadership
11. Technology Integration
12. Community Resilience
13. International Coordination
14. Specialized Disasters

## Error Handling & Recovery

### Robust Loading Strategies

1. **Primary**: MPS (Apple Silicon) with bfloat16
2. **Fallback 1**: CPU with bfloat16
3. **Fallback 2**: Auto device with float32

### Memory Management

- Gradient checkpointing enabled
- Memory monitoring every 10 steps
- Automatic garbage collection at 80% usage
- MPS cache clearing when needed

### Training Monitoring

- Real-time loss tracking
- Memory usage alerts
- Progress checkpoints
- Validation during training

## Output Structure

### Trained Model Location

```
./models/emergency_relief_fine_tuned/
├── emergency_relief_model/          # Fine-tuned model
│   ├── config.json
│   ├── pytorch_model.bin
│   ├── tokenizer.json
│   └── training_config.json
└── logs/                            # Training logs
    └── training_[timestamp].log
```

### API Endpoints (After Deployment)

- `GET /health` - Health check
- `POST /emergency-guidance` - Get emergency advice
- `GET /test` - Test with sample scenario

## Validation Criteria

### Success Metrics

- **Response Accuracy**: 95%+ on emergency scenarios
- **Emergency Relevance**: 100% emergency-focused responses
- **Safety Focus**: 100% safety-prioritized guidance
- **Actionable Guidance**: 90%+ step-by-step procedures

### Quality Assessment

- Professional emergency management language
- Adherence to FEMA, WHO, Red Cross standards
- Clear, actionable step-by-step guidance
- Safety-first approach in all responses

## Troubleshooting

### Common Issues & Solutions

1. **Memory Issues**

   - Reduce batch_size to 1
   - Enable gradient_accumulation_steps
   - Close unnecessary applications

2. **Model Loading Failures**

   - Script includes multiple fallback strategies
   - Automatic device detection and optimization
   - Comprehensive error logging

3. **Training Interruption**
   - Automatic checkpointing preserves progress
   - Resume from last checkpoint available
   - Model state saved every 100 steps

## Next Steps After Training

1. **Validate Model**: Run comprehensive test suite
2. **Deploy API**: Start Flask API server for inference
3. **Integration**: Connect to emergency management systems
4. **Monitoring**: Track model performance in production
5. **Updates**: Regular retraining with new emergency scenarios

## Support & Resources

- **Training Logs**: Check `./models/emergency_relief_fine_tuned/logs/`
- **Configuration**: `./config/emergency_relief_training_config.json`
- **Validation**: `scripts/validate_training_pipeline.py`
- **Testing**: `scripts/test_emergency_relief_model.py`

---

**Status**: COMPLETED All components validated and ready for training
**Hardware**: COMPLETED M4 MacBook Pro optimal configuration detected  
**Estimated Training Time**: 1-3 hours
**Success Probability**: High (robust error handling and fallbacks)
