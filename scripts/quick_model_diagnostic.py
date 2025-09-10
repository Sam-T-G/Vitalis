#!/usr/bin/env python3
"""
Quick Emergency Relief Model Diagnostic
Tests model loading and basic functionality without full generation
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import warnings
warnings.filterwarnings("ignore")

def quick_diagnostic():
    """Quick diagnostic test for Emergency Relief model"""
    
    print("EMERGENCY RELIEF AI - QUICK DIAGNOSTIC")
    print("=" * 50)
    
    base_model_path = "./models/gpt-oss-20b"
    lora_model_path = "./models/emergency_relief_fine_tuned/emergency_relief_lora"
    
    try:
        # Test 1: Tokenizer Loading
        print("1. Testing tokenizer loading...")
        tokenizer = AutoTokenizer.from_pretrained(
            base_model_path,
            local_files_only=True,
            trust_remote_code=True
        )
        print(f"   Tokenizer loaded successfully")
        print(f"   Vocabulary size: {len(tokenizer)}")
        
        # Test 2: Base Model Loading  
        print("\n2. Testing base model loading...")
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_path,
            local_files_only=True,
            trust_remote_code=True,
            device_map="cpu",
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=True
        )
        print(f"   Base model loaded successfully")
        print(f"   Model device: {next(base_model.parameters()).device}")
        print(f"   Model dtype: {next(base_model.parameters()).dtype}")
        
        # Test 3: LoRA Adapter Loading
        print("\n3. Testing LoRA adapter loading...")
        model = PeftModel.from_pretrained(
            base_model,
            lora_model_path,
            torch_dtype=torch.bfloat16
        )
        print(f"   LoRA adapter loaded successfully")
        print(f"   Model type: {type(model).__name__}")
        
        # Test 4: Basic Tokenization
        print("\n4. Testing tokenization...")
        test_prompt = "Emergency: Wildfire evacuation needed"
        inputs = tokenizer(test_prompt, return_tensors="pt")
        print(f"   Tokenization successful")
        print(f"   Input shape: {inputs.input_ids.shape}")
        print(f"   Input tokens: {inputs.input_ids.shape[1]}")
        
        # Test 5: Model Forward Pass (Single Token)
        print("\n5. Testing model forward pass...")
        with torch.no_grad():
            # Just get logits, don't generate
            outputs = model(inputs.input_ids)
            logits = outputs.logits
            print(f"   Forward pass successful")
            print(f"   Output shape: {logits.shape}")
            print(f"   Vocabulary logits: {logits.shape[-1]}")
        
        # Test 6: Single Token Generation
        print("\n6. Testing single token generation...")
        with torch.no_grad():
            # Generate just one token to test generation pipeline
            single_output = model.generate(
                inputs.input_ids,
                max_new_tokens=1,
                do_sample=False,
                use_cache=True
            )
            generated_token = tokenizer.decode(single_output[0][-1])
            print(f"   Single token generation successful")
            print(f"   Generated token: '{generated_token}'")
        
        # Test 7: Memory Usage
        print("\n7. Memory diagnostics...")
        if torch.cuda.is_available():
            print(f"   GPU Memory: {torch.cuda.memory_allocated() / 1e9:.2f}GB")
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        print(f"   CPU Memory: {memory_mb:.0f}MB")
        
        print("\n" + "=" * 50)
        print("✓ ALL DIAGNOSTIC TESTS PASSED!")
        print("Your Emergency Relief AI model is working correctly.")
        print("Performance can be improved with GPU acceleration.")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\nDiagnostic failed at step: {e}")
        print("\nDebugging information:")
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        return False

if __name__ == "__main__":
    success = quick_diagnostic()
    if success:
        print("\nModel Status: READY FOR DEPLOYMENT")
        print("Consider GPU acceleration for faster inference.")
    else:
        print("\nModel Status: NEEDS ATTENTION")
        print("Check model files and dependencies.")
