#!/usr/bin/env python3
"""
Emergency Relief AI Training Launcher
Simple script to launch the complete training pipeline
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from vitalis.training.emergency_relief_trainer import EmergencyReliefTrainer

def check_prerequisites():
    """Check that all prerequisites are met before training"""
    print("SEARCH Checking prerequisites...")
    
    # Check Python environment
    try:
        import torch
        import transformers
        print(f"COMPLETED PyTorch {torch.__version__}")
        print(f"COMPLETED Transformers {transformers.__version__}")
    except ImportError as e:
        print(f"FAILED Missing dependency: {e}")
        return False
    
    # Check Apple Silicon MPS availability
    if torch.backends.mps.is_available():
        print("COMPLETED Apple Silicon MPS available")
    else:
        print("WARNING  MPS not available, will use CPU")
    
    # Check required files
    required_files = [
        "./models/gpt-oss-20b/config.json",
        "./data/ENHANCED_EMERGENCY_RELIEF_TRAINING_DATA.json",
        "./config/emergency_relief_training_config.json"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"COMPLETED {file_path}")
        else:
            print(f"FAILED Missing: {file_path}")
            return False
    
    # Check available memory
    try:
        import psutil
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        print(f"COMPLETED System memory: {memory_gb:.1f}GB")
        
        if memory_gb < 16:
            print("WARNING  Warning: Less than 16GB RAM detected. Training may be slow.")
        
    except ImportError:
        print("WARNING  Cannot check system memory (psutil not available)")
    
    print("COMPLETED Prerequisites check completed")
    return True

def estimate_training_time():
    """Estimate training time based on system and data"""
    try:
        # Load training data to count examples
        with open("./data/ENHANCED_EMERGENCY_RELIEF_TRAINING_DATA.json", 'r') as f:
            data = json.load(f)
        
        num_examples = len(data.get('training_data', []))
        
        # Load config for training parameters
        with open("./config/emergency_relief_training_config.json", 'r') as f:
            config = json.load(f)
        
        epochs = config.get('num_epochs', 3)
        batch_size = config.get('batch_size', 1)
        grad_accum = config.get('gradient_accumulation_steps', 4)
        
        # Rough estimation
        steps_per_epoch = (num_examples // (batch_size * grad_accum)) + 1
        total_steps = steps_per_epoch * epochs
        
        # Estimate time per step (Apple Silicon M4)
        time_per_step = 15  # seconds (conservative estimate)
        total_time_hours = (total_steps * time_per_step) / 3600
        
        print(f"METRICS Training estimation:")
        print(f"   Examples: {num_examples}")
        print(f"   Epochs: {epochs}")
        print(f"   Steps per epoch: {steps_per_epoch}")
        print(f"   Total steps: {total_steps}")
        print(f"   Estimated time: {total_time_hours:.1f} hours")
        
        return total_time_hours
        
    except Exception as e:
        print(f"WARNING  Could not estimate training time: {e}")
        return None

def main():
    """Main training launcher"""
    print("LAUNCH EMERGENCY RELIEF AI TRAINING LAUNCHER")
    print("=" * 60)
    
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"FOLDER Working directory: {os.getcwd()}")
    
    # Check prerequisites
    if not check_prerequisites():
        print("\nFAILED Prerequisites check failed. Please fix issues before training.")
        return 1
    
    # Estimate training time
    estimated_time = estimate_training_time()
    
    # Confirm before starting
    print("\n" + "=" * 60)
    print("TARGET READY TO START TRAINING")
    print("=" * 60)
    
    if estimated_time:
        print(f"TIME  Estimated training time: {estimated_time:.1f} hours")
    
    print("CHECKLIST What will happen:")
    print("   1. Load GPT-OSS 20B model")
    print("   2. Prepare emergency relief training data")
    print("   3. Fine-tune model for emergency relief scenarios")
    print("   4. Validate trained model")
    print("   5. Save fine-tuned model")
    
    print("\nWARNING  Important notes:")
    print("   - Keep your MacBook plugged in")
    print("   - Close unnecessary applications")
    print("   - Training will use significant system resources")
    print("   - Do not interrupt the training process")
    
    # Ask for confirmation
    response = input("\nQUESTION Continue with training? (y/N): ").strip().lower()
    
    if response not in ['y', 'yes']:
        print("FAILED Training cancelled by user")
        return 0
    
    # Start training
    print("\nLAUNCH Starting training pipeline...")
    print("=" * 60)
    
    try:
        # Create trainer and run pipeline
        config_path = "./config/emergency_relief_training_config.json"
        trainer = EmergencyReliefTrainer(config_path)
        success = trainer.run_complete_pipeline()
        
        if success:
            print("\nSUCCESS TRAINING COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print(f"FOLDER Model saved to: {trainer.config['output_dir']}/emergency_relief_model")
            print("SEARCH Check the logs for detailed training information")
            print("LAUNCH Your emergency relief AI is ready for deployment!")
            return 0
        else:
            print("\nFAILED TRAINING FAILED")
            print("=" * 60)
            print("SEARCH Check the logs for error details")
            print("IDEA Try adjusting batch size or model loading strategy")
            return 1
            
    except KeyboardInterrupt:
        print("\nWARNING  Training interrupted by user")
        return 1
    except Exception as e:
        print(f"\nFAILED Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
