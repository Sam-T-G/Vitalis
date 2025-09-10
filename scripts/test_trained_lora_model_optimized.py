#!/usr/bin/env python3
"""
Optimized Emergency Relief LoRA Model Test Script
Uses modern inference best practices for MoE models
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from peft import PeftModel
import warnings
import gc
import time
warnings.filterwarnings("ignore")

def clear_memory():
    """Clear GPU and system memory"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()

def test_emergency_relief_optimized():
    """Test the trained LoRA emergency relief model with optimizations"""
    
    print("TESTING TRAINED EMERGENCY RELIEF AI (OPTIMIZED)")
    print("=" * 60)
    
    # Paths
    base_model_path = "./models/gpt-oss-20b"
    lora_model_path = "./models/emergency_relief_fine_tuned/emergency_relief_lora"
    
    print("Loading base model and LoRA adapter...")
    print("Note: Using CPU-only inference for stability")
    
    try:
        # Clear memory before loading
        clear_memory()
        
        # Load tokenizer with optimized settings
        tokenizer = AutoTokenizer.from_pretrained(
            base_model_path,
            local_files_only=True,
            trust_remote_code=True
        )
        
        # Proper tokenizer configuration for MoE models
        if tokenizer.pad_token is None:
            tokenizer.pad_token = "<|endoftext|>"
            tokenizer.pad_token_id = 199999
        
        tokenizer.padding_side = "left"
        
        print(f"Tokenizer loaded. Vocab size: {len(tokenizer)}")
        print(f"EOS token: {tokenizer.eos_token} (ID: {tokenizer.eos_token_id})")
        print(f"PAD token: {tokenizer.pad_token} (ID: {tokenizer.pad_token_id})")
        
        # Load base model with optimized settings
        print("Loading base model (this may take a few minutes)...")
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_path,
            local_files_only=True,
            trust_remote_code=True,
            device_map="cpu",  # Force CPU to avoid GPU memory issues
            torch_dtype=torch.bfloat16,  # Use bfloat16 to match model default
            low_cpu_mem_usage=True,
            use_safetensors=True
        )
        
        # Optimize model for inference
        base_model.eval()
        
        # Load LoRA adapter with matching dtype
        print("Loading LoRA adapter...")
        model = PeftModel.from_pretrained(
            base_model,
            lora_model_path,
            torch_dtype=torch.bfloat16  # Match base model dtype
        )
        
        # Configure generation settings optimized for MoE
        generation_config = GenerationConfig(
            max_new_tokens=100,  # Reduced for faster generation
            min_new_tokens=5,
            temperature=0.3,     # Lower temperature for more focused output
            do_sample=True,
            top_p=0.8,          # Nucleus sampling
            top_k=40,           # Top-k sampling
            repetition_penalty=1.05,  # Slight repetition penalty
            length_penalty=1.0,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=[200002, 199999],  # Primary EOS tokens
            use_cache=True,
            output_scores=False,
            return_dict_in_generate=False
        )
        
        print("Emergency Relief LoRA model loaded successfully!")
        print(f"Model loaded on: {next(model.parameters()).device}")
        
        # Test scenarios - reduced for efficiency
        test_scenarios = [
            "How do you coordinate evacuation during a wildfire?",
            "What are essential emergency shelter supplies?"
        ]
        
        print(f"\nTesting {len(test_scenarios)} Emergency Relief Scenarios:")
        print("=" * 60)
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n{i}. SCENARIO: {scenario}")
            print("-" * 50)
            
            try:
                # Clear memory before each generation
                clear_memory()
                
                # Simple prompt format for better compatibility
                prompt = f"Emergency Relief Coordinator: {scenario}\n\nResponse:"
                
                # Tokenize with proper settings
                inputs = tokenizer(
                    prompt,
                    return_tensors="pt",
                    padding=False,  # No padding for single input
                    truncation=True,
                    max_length=1024  # Reduced context length
                )
                
                print("Generating emergency guidance...")
                start_time = time.time()
                
                # Generate with timeout and error handling
                with torch.no_grad():
                    try:
                        # Set a manual timeout using threading
                        import threading
                        import queue
                        
                        result_queue = queue.Queue()
                        
                        def generate_worker():
                            try:
                                outputs = model.generate(
                                    inputs.input_ids,
                                    generation_config=generation_config,
                                    attention_mask=inputs.get('attention_mask', None)
                                )
                                result_queue.put(('success', outputs))
                            except Exception as e:
                                result_queue.put(('error', str(e)))
                        
                        # Start generation in separate thread
                        thread = threading.Thread(target=generate_worker)
                        thread.daemon = True
                        thread.start()
                        
                        # Wait for result with timeout
                        thread.join(timeout=30)  # 30 second timeout
                        
                        if thread.is_alive():
                            print("Generation timed out after 30 seconds")
                            response_only = "Emergency response generation timed out. This may indicate model compatibility issues."
                        else:
                            try:
                                result_type, result = result_queue.get_nowait()
                                if result_type == 'success':
                                    # Decode response
                                    generated_text = tokenizer.decode(result[0], skip_special_tokens=True)
                                    response_only = generated_text[len(prompt):].strip()
                                    
                                    # Clean up response
                                    if response_only:
                                        # Remove any remaining special tokens
                                        for token in ["<|return|>", "<|endoftext|>", "<|call|>"]:
                                            response_only = response_only.replace(token, "")
                                        response_only = response_only.strip()
                                    
                                    if not response_only or len(response_only) < 5:
                                        response_only = "Generated response was too short or empty."
                                else:
                                    print(f"Generation error: {result}")
                                    response_only = "Emergency response generation encountered an error."
                            except queue.Empty:
                                response_only = "Emergency response generation failed to complete."
                        
                        generation_time = time.time() - start_time
                        print(f"Generation time: {generation_time:.2f}s")
                        
                    except Exception as e:
                        print(f"Generation failed: {e}")
                        response_only = "Emergency response generation failed due to technical issues."
                
                print(f"\nEMERGENCY RELIEF GUIDANCE:")
                print(f"{response_only}")
                print("-" * 50)
                
                # Basic quality assessment
                if "emergency" in response_only.lower() or "evacuation" in response_only.lower():
                    print("Quality: Relevant emergency response generated")
                elif len(response_only) > 20:
                    print("Quality: Response generated but may need review")
                else:
                    print("Quality: Response quality needs improvement")
                
            except Exception as e:
                print(f"Scenario {i} failed: {e}")
                continue
        
        print("\n" + "=" * 60)
        print("EMERGENCY RELIEF AI TESTING COMPLETE!")
        print("=" * 60)
        
        # Cleanup
        del model
        del base_model
        clear_memory()
        
        return True
        
    except Exception as e:
        print(f"Testing failed: {e}")
        print("\nDebugging information:")
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
        
        return False

if __name__ == "__main__":
    success = test_emergency_relief_optimized()
    if success:
        print("\nOptimized testing completed successfully!")
    else:
        print("\nTesting encountered issues - check model configuration")
