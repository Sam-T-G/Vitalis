#!/usr/bin/env python3
"""
LoRA Emergency Relief AI Training Launcher
Memory-efficient training using Parameter-Efficient Fine-Tuning (LoRA)
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from vitalis.training.lora_emergency_trainer import LoRAEmergencyTrainer

def main():
    """Main LoRA training launcher"""
    print("LAUNCH MEMORY-EFFICIENT EMERGENCY RELIEF AI TRAINING")
    print("Using LoRA (Low-Rank Adaptation) for Parameter-Efficient Fine-Tuning")
    print("=" * 70)
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"FOLDER Working directory: {os.getcwd()}")
    
    print("\nIDEA LoRA Training Benefits:")
    print("   COMPLETED Uses ~90% less memory than full fine-tuning")
    print("   COMPLETED Trains only ~0.1% of model parameters")
    print("   COMPLETED Maintains model quality for specialized tasks")
    print("   COMPLETED Compatible with quantized models")
    print("   COMPLETED Fast training and inference")
    
    print("\nMETRICS Expected Performance:")
    print("   SAVE Memory usage: ~8-12GB (vs 40-70GB for full training)")
    print("   TIME  Training time: ~10-15 minutes (vs hours for full training)")
    print("   TARGET Quality: Excellent for domain specialization")
    
    # Confirm before starting
    response = input("\nQUESTION Start LoRA emergency relief training? (y/N): ").strip().lower()
    
    if response not in ['y', 'yes']:
        print("FAILED Training cancelled by user")
        return 0
    
    print("\nLAUNCH Starting LoRA training pipeline...")
    print("=" * 70)
    
    try:
        config_path = "./config/emergency_relief_training_config.json"
        trainer = LoRAEmergencyTrainer(config_path)
        success = trainer.run_complete_pipeline()
        
        if success:
            print("\nSUCCESS LORA EMERGENCY RELIEF TRAINING COMPLETED!")
            print("=" * 70)
            print(f"FOLDER LoRA adapter saved to: {trainer.config['output_dir']}/emergency_relief_lora")
            print("SEARCH Check the logs for detailed training information")
            print("LAUNCH Your memory-efficient emergency relief AI is ready!")
            
            print("\nCHECKLIST Next steps:")
            print("   1. Test the model: python scripts/test_lora_emergency_model.py")
            print("   2. Deploy API: python scripts/deploy_lora_emergency_api.py")
            
            return 0
        else:
            print("\nFAILED LORA TRAINING FAILED")
            print("=" * 70)
            print("SEARCH Check the logs for error details")
            return 1
            
    except KeyboardInterrupt:
        print("\nWARNING  Training interrupted by user")
        return 1
    except Exception as e:
        print(f"\nFAILED Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
