"""
GPT-OSS 20B Model Test Script for Emergency Relief AI
Updated to handle MoE model loading issues and Apple Silicon optimization
"""

from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
import torch
import os
import warnings
warnings.filterwarnings("ignore")

def test_model_loading():
    """Test GPT-OSS 20B model loading and basic inference"""
    
    print("Testing GPT-OSS 20B Model Loading...")
    print("=" * 50)
    
    # Model path
    model_path = "./models/gpt-oss-20b"
    
    try:
        # Step 1: Load tokenizer
        print("1. Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_path, 
            local_files_only=True,
            trust_remote_code=True
        )
        print("   COMPLETED Tokenizer loaded successfully")
        
        # Step 2: Load model with better error handling
        print("2. Loading model...")
        
        # Try different loading strategies
        loading_strategies = [
            {
                "name": "Standard Loading",
                "kwargs": {
                    "torch_dtype": torch.bfloat16,
                    "device_map": "auto",
                    "low_cpu_mem_usage": True,
                    "local_files_only": True,
                    "trust_remote_code": True
                }
            },
            {
                "name": "CPU Only Loading",
                "kwargs": {
                    "torch_dtype": torch.bfloat16,
                    "device_map": "cpu",
                    "low_cpu_mem_usage": True,
                    "local_files_only": True,
                    "trust_remote_code": True
                }
            },
            {
                "name": "Float32 Loading",
                "kwargs": {
                    "torch_dtype": torch.float32,
                    "device_map": "auto",
                    "low_cpu_mem_usage": True,
                    "local_files_only": True,
                    "trust_remote_code": True
                }
            }
        ]
        
        model = None
        successful_strategy = None
        
        for strategy in loading_strategies:
            print(f"   Trying: {strategy['name']}")
            try:
                model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    **strategy['kwargs']
                )
                successful_strategy = strategy['name']
                print(f"   COMPLETED Model loaded successfully with {strategy['name']}")
                break
            except Exception as e:
                print(f"   FAILED {strategy['name']} failed: {str(e)[:100]}...")
                continue
        
        if model is None:
            print("FAILED All loading strategies failed")
            return False
            
        # Step 3: Test basic inference
        print("3. Testing basic inference...")
        
        # Simple emergency relief prompt
        prompt = "What are the basic steps for setting up an emergency shelter?"
        
        # Tokenize input
        inputs = tokenizer(prompt, return_tensors="pt")
        
        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                max_new_tokens=100,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decode response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        print("   COMPLETED Inference successful")
        print("\n" + "="*50)
        print("MODEL TEST RESULTS")
        print("="*50)
        print(f"Loading Strategy: {successful_strategy}")
        print(f"Model Type: {type(model).__name__}")
        print(f"Model Device: {next(model.parameters()).device}")
        print(f"Model Dtype: {next(model.parameters()).dtype}")
        
        print("\nSample Generation:")
        print("-" * 30)
        print(f"Prompt: {prompt}")
        print(f"Response: {response[len(prompt):].strip()}")
        
        return True
        
    except Exception as e:
        print(f"FAILED Model test failed: {str(e)}")
        return False

def test_emergency_scenarios():
    """Test specific emergency relief scenarios"""
    
    emergency_prompts = [
        "How do you coordinate evacuation during a wildfire?",
        "What supplies are needed for emergency shelter setup?",
        "How do you manage volunteers during disaster response?",
        "What are the steps for medical triage in mass casualties?"
    ]
    
    print("\n" + "="*50)
    print("EMERGENCY SCENARIO TESTING")
    print("="*50)
    
    model_path = "./models/gpt-oss-20b"
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(
            model_path, 
            local_files_only=True,
            trust_remote_code=True
        )
        
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            low_cpu_mem_usage=True,
            local_files_only=True,
            trust_remote_code=True
        )
        
        for i, prompt in enumerate(emergency_prompts, 1):
            print(f"\n{i}. Testing: {prompt}")
            
            inputs = tokenizer(prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = model.generate(
                    inputs.input_ids,
                    max_new_tokens=80,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"   Response: {response[len(prompt):].strip()[:150]}...")
            
    except Exception as e:
        print(f"FAILED Emergency scenario testing failed: {str(e)}")

if __name__ == "__main__":
    # Run basic model test
    success = test_model_loading()
    
    if success:
        print("\nSUCCESS Model is ready for emergency relief training!")
        
        # Run emergency scenario tests
        test_emergency_scenarios()
    else:
        print("\nWARNING  Model loading issues detected. Consider using LM Studio for training.")
