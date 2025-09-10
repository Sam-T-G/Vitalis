#!/usr/bin/env python3
"""
Deep Generation Audit Script
Systematically test generation to identify the exact timeout cause
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from peft import PeftModel
import warnings
import time
import gc
import threading
import queue
import psutil
import os
warnings.filterwarnings("ignore")

class DeepGenerationAuditor:
    """Deep audit of generation process to identify timeout causes"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.base_model = None
        self.loaded = False
        
    def clear_memory(self):
        """Clear memory and collect garbage"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
        
    def get_memory_usage(self):
        """Get current memory usage"""
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        return memory_mb
    
    def load_model(self):
        """Load model with detailed logging"""
        base_model_path = "./models/gpt-oss-20b"
        lora_model_path = "./models/emergency_relief_fine_tuned/emergency_relief_lora"
        
        print("=" * 60)
        print("DEEP GENERATION AUDIT - MODEL LOADING")
        print("=" * 60)
        
        try:
            self.clear_memory()
            start_memory = self.get_memory_usage()
            print(f"Starting memory: {start_memory:.0f}MB")
            
            # Load tokenizer
            print("\n1. Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                base_model_path,
                local_files_only=True,
                trust_remote_code=True
            )
            
            # Tokenizer configuration analysis
            print("   Tokenizer analysis:")
            print(f"   - Vocab size: {len(self.tokenizer)}")
            print(f"   - EOS token: {self.tokenizer.eos_token} (ID: {self.tokenizer.eos_token_id})")
            print(f"   - PAD token: {self.tokenizer.pad_token} (ID: {self.tokenizer.pad_token_id})")
            print(f"   - BOS token: {self.tokenizer.bos_token} (ID: {self.tokenizer.bos_token_id})")
            
            # Fix tokenizer configuration
            if self.tokenizer.pad_token is None or self.tokenizer.pad_token_id == self.tokenizer.eos_token_id:
                print("   - Fixing pad token configuration...")
                self.tokenizer.pad_token = "<|endoftext|>"
                self.tokenizer.pad_token_id = 199999
            
            self.tokenizer.padding_side = "left"
            print(f"   - Updated PAD token: {self.tokenizer.pad_token} (ID: {self.tokenizer.pad_token_id})")
            
            tokenizer_memory = self.get_memory_usage()
            print(f"   - Memory after tokenizer: {tokenizer_memory:.0f}MB (+{tokenizer_memory - start_memory:.0f}MB)")
            
            # Load base model
            print("\n2. Loading base model...")
            self.base_model = AutoModelForCausalLM.from_pretrained(
                base_model_path,
                local_files_only=True,
                trust_remote_code=True,
                device_map="cpu",
                torch_dtype=torch.bfloat16,
                low_cpu_mem_usage=True
            )
            
            base_model_memory = self.get_memory_usage()
            print(f"   - Memory after base model: {base_model_memory:.0f}MB (+{base_model_memory - tokenizer_memory:.0f}MB)")
            
            # Model configuration analysis
            print("   Base model analysis:")
            print(f"   - Model type: {type(self.base_model).__name__}")
            print(f"   - Device: {next(self.base_model.parameters()).device}")
            print(f"   - Dtype: {next(self.base_model.parameters()).dtype}")
            print(f"   - Vocab size: {self.base_model.config.vocab_size}")
            print(f"   - Hidden layers: {self.base_model.config.num_hidden_layers}")
            print(f"   - Attention heads: {self.base_model.config.num_attention_heads}")
            print(f"   - MoE experts: {self.base_model.config.num_local_experts}")
            print(f"   - Active experts: {self.base_model.config.num_experts_per_tok}")
            
            # Load LoRA adapter
            print("\n3. Loading LoRA adapter...")
            self.model = PeftModel.from_pretrained(
                self.base_model,
                lora_model_path,
                torch_dtype=torch.bfloat16
            )
            
            final_memory = self.get_memory_usage()
            print(f"   - Memory after LoRA: {final_memory:.0f}MB (+{final_memory - base_model_memory:.0f}MB)")
            print(f"   - Total memory used: {final_memory - start_memory:.0f}MB")
            
            # LoRA analysis
            print("   LoRA adapter analysis:")
            print(f"   - Model type: {type(self.model).__name__}")
            print(f"   - Active adapters: {list(self.model.peft_config.keys())}")
            
            # Set to eval mode
            self.model.eval()
            
            print("\nSUCCESS: Model loading completed successfully!")
            self.loaded = True
            return True
            
        except Exception as e:
            print(f"ERROR: Model loading failed: {e}")
            return False
    
    def test_tokenization(self):
        """Test tokenization process"""
        print("\n" + "=" * 60)
        print("TOKENIZATION TESTS")
        print("=" * 60)
        
        test_inputs = [
            "Hello",
            "Emergency: Fire evacuation needed",
            "How do you coordinate evacuation during a wildfire?",
            "EMERGENCY SITUATION: A fast-moving wildfire is approaching our residential area."
        ]
        
        for i, text in enumerate(test_inputs, 1):
            print(f"\n{i}. Testing: '{text}'")
            
            try:
                # Basic tokenization
                tokens = self.tokenizer.encode(text)
                print(f"   - Token count: {len(tokens)}")
                print(f"   - Token IDs: {tokens[:10]}{'...' if len(tokens) > 10 else ''}")
                
                # Tokenization with return tensors
                inputs = self.tokenizer(text, return_tensors="pt")
                print(f"   - Input shape: {inputs.input_ids.shape}")
                print(f"   - Has attention mask: {'attention_mask' in inputs}")
                
                # Decode back
                decoded = self.tokenizer.decode(tokens)
                print(f"   - Decode matches: {decoded.strip() == text.strip()}")
                
            except Exception as e:
                print(f"   ERROR: Tokenization failed: {e}")
    
    def test_forward_pass(self):
        """Test model forward pass"""
        print("\n" + "=" * 60)
        print("FORWARD PASS TESTS")
        print("=" * 60)
        
        if not self.loaded:
            print("ERROR: Model not loaded")
            return
        
        test_text = "Emergency evacuation"
        
        try:
            print(f"Testing forward pass with: '{test_text}'")
            
            # Tokenize
            inputs = self.tokenizer(test_text, return_tensors="pt")
            print(f"Input shape: {inputs.input_ids.shape}")
            
            start_memory = self.get_memory_usage()
            start_time = time.time()
            
            # Forward pass
            with torch.no_grad():
                outputs = self.model(inputs.input_ids)
                logits = outputs.logits
            
            forward_time = time.time() - start_time
            end_memory = self.get_memory_usage()
            
            print(f"SUCCESS: Forward pass successful!")
            print(f"   - Output shape: {logits.shape}")
            print(f"   - Time: {forward_time:.3f}s")
            print(f"   - Memory change: +{end_memory - start_memory:.0f}MB")
            
            # Test next token prediction
            next_token_logits = logits[0, -1, :]
            next_token_id = torch.argmax(next_token_logits).item()
            next_token = self.tokenizer.decode([next_token_id])
            print(f"   - Predicted next token: '{next_token}' (ID: {next_token_id})")
            
            return True
            
        except Exception as e:
            print(f"ERROR: Forward pass failed: {e}")
            return False
    
    def test_incremental_generation(self):
        """Test generation with increasing token counts"""
        print("\n" + "=" * 60)
        print("INCREMENTAL GENERATION TESTS")
        print("=" * 60)
        
        if not self.loaded:
            print("ERROR: Model not loaded")
            return
        
        test_text = "Emergency evacuation"
        token_counts = [1, 2, 3, 5, 10]
        
        for max_tokens in token_counts:
            print(f"\nTesting generation with {max_tokens} tokens...")
            
            try:
                inputs = self.tokenizer(test_text, return_tensors="pt")
                
                start_memory = self.get_memory_usage()
                start_time = time.time()
                
                # Use threading for timeout
                result_queue = queue.Queue()
                
                def generate_worker():
                    try:
                        with torch.no_grad():
                            outputs = self.model.generate(
                                inputs.input_ids,
                                attention_mask=inputs.get('attention_mask', None),
                                max_new_tokens=max_tokens,
                                min_new_tokens=1,
                                do_sample=False,  # Deterministic for testing
                                use_cache=True,
                                pad_token_id=self.tokenizer.pad_token_id,
                                eos_token_id=[200002, 199999, 200012]
                            )
                        result_queue.put(('success', outputs))
                    except Exception as e:
                        result_queue.put(('error', str(e)))
                
                thread = threading.Thread(target=generate_worker)
                thread.daemon = True
                thread.start()
                
                # Wait with timeout
                timeout_seconds = 5 + max_tokens  # Scale timeout with token count
                thread.join(timeout=timeout_seconds)
                
                generation_time = time.time() - start_time
                end_memory = self.get_memory_usage()
                
                if thread.is_alive():
                    print(f"   TIMEOUT after {timeout_seconds}s")
                    print(f"   - This is where the problem occurs!")
                    return False
                else:
                    try:
                        result_type, result = result_queue.get_nowait()
                        if result_type == 'success':
                            generated_text = self.tokenizer.decode(result[0], skip_special_tokens=True)
                            new_text = generated_text[len(test_text):].strip()
                            
                            print(f"   SUCCESS in {generation_time:.3f}s")
                            print(f"   - Generated: '{new_text}'")
                            print(f"   - Memory change: +{end_memory - start_memory:.0f}MB")
                            print(f"   - Output length: {result[0].shape[1]} tokens")
                        else:
                            print(f"   ERROR: Generation error: {result}")
                            return False
                    except queue.Empty:
                        print(f"   ERROR: No result returned")
                        return False
                        
            except Exception as e:
                print(f"   ERROR: Test setup failed: {e}")
                return False
        
        print("\nSUCCESS: All incremental generation tests passed!")
        return True
    
    def test_generation_strategies(self):
        """Test different generation strategies"""
        print("\n" + "=" * 60)
        print("GENERATION STRATEGY TESTS")
        print("=" * 60)
        
        if not self.loaded:
            print("ERROR: Model not loaded")
            return
        
        test_text = "Emergency evacuation"
        strategies = [
            {
                "name": "Greedy (no sampling)",
                "params": {
                    "max_new_tokens": 5,
                    "do_sample": False,
                    "use_cache": True
                }
            },
            {
                "name": "Low temperature sampling",
                "params": {
                    "max_new_tokens": 5,
                    "do_sample": True,
                    "temperature": 0.1,
                    "use_cache": True
                }
            },
            {
                "name": "Without cache",
                "params": {
                    "max_new_tokens": 3,
                    "do_sample": False,
                    "use_cache": False
                }
            },
            {
                "name": "With top_k",
                "params": {
                    "max_new_tokens": 3,
                    "do_sample": True,
                    "top_k": 10,
                    "temperature": 0.5,
                    "use_cache": True
                }
            }
        ]
        
        for strategy in strategies:
            print(f"\nTesting: {strategy['name']}")
            
            try:
                inputs = self.tokenizer(test_text, return_tensors="pt")
                
                # Add required parameters
                params = strategy['params'].copy()
                params.update({
                    "pad_token_id": self.tokenizer.pad_token_id,
                    "eos_token_id": [200002, 199999, 200012],
                    "attention_mask": inputs.get('attention_mask', None)
                })
                
                start_time = time.time()
                
                # Use timeout for each strategy
                result_queue = queue.Queue()
                
                def generate_worker():
                    try:
                        with torch.no_grad():
                            outputs = self.model.generate(inputs.input_ids, **params)
                        result_queue.put(('success', outputs))
                    except Exception as e:
                        result_queue.put(('error', str(e)))
                
                thread = threading.Thread(target=generate_worker)
                thread.daemon = True
                thread.start()
                thread.join(timeout=10)  # 10 second timeout
                
                generation_time = time.time() - start_time
                
                if thread.is_alive():
                    print(f"   TIMEOUT after 10s")
                else:
                    try:
                        result_type, result = result_queue.get_nowait()
                        if result_type == 'success':
                            generated_text = self.tokenizer.decode(result[0], skip_special_tokens=True)
                            new_text = generated_text[len(test_text):].strip()
                            print(f"   SUCCESS in {generation_time:.3f}s")
                            print(f"   - Generated: '{new_text}'")
                        else:
                            print(f"   ERROR: {result}")
                    except queue.Empty:
                        print(f"   ERROR: No result")
                        
            except Exception as e:
                print(f"   ERROR: Setup failed: {e}")
    
    def test_minimal_generation(self):
        """Test the most minimal generation possible"""
        print("\n" + "=" * 60)
        print("MINIMAL GENERATION TEST")
        print("=" * 60)
        
        if not self.loaded:
            print("ERROR: Model not loaded")
            return
        
        print("Testing absolute minimal generation...")
        
        try:
            # Single token input
            input_ids = torch.tensor([[199998]])  # BOS token
            
            print(f"Input: {input_ids}")
            print(f"Input shape: {input_ids.shape}")
            
            start_time = time.time()
            
            # Most minimal generation
            with torch.no_grad():
                # Direct generation call with minimal parameters
                outputs = self.model.generate(
                    input_ids,
                    max_length=input_ids.shape[1] + 1,  # Just one more token
                    do_sample=False,
                    pad_token_id=199999,
                    eos_token_id=200002
                )
            
            generation_time = time.time() - start_time
            
            print(f"SUCCESS: Minimal generation successful in {generation_time:.3f}s")
            print(f"Output: {outputs}")
            print(f"Output shape: {outputs.shape}")
            
            # Decode
            decoded = self.tokenizer.decode(outputs[0])
            print(f"Decoded: '{decoded}'")
            
            return True
            
        except Exception as e:
            print(f"ERROR: Minimal generation failed: {e}")
            return False
    
    def run_full_audit(self):
        """Run complete generation audit"""
        print("STARTING DEEP GENERATION AUDIT")
        print("This will systematically test every aspect of generation")
        print("to identify the exact cause of timeouts.\n")
        
        # Step 1: Load model
        if not self.load_model():
            print("ERROR: Audit failed: Cannot load model")
            return False
        
        # Step 2: Test tokenization
        self.test_tokenization()
        
        # Step 3: Test forward pass
        if not self.test_forward_pass():
            print("ERROR: Audit failed: Forward pass issues")
            return False
        
        # Step 4: Test minimal generation
        if not self.test_minimal_generation():
            print("ERROR: Audit failed: Even minimal generation fails")
            return False
        
        # Step 5: Test incremental generation
        if not self.test_incremental_generation():
            print("ERROR: Found the problem in incremental generation!")
            return False
        
        # Step 6: Test different strategies
        self.test_generation_strategies()
        
        print("\n" + "=" * 60)
        print("AUDIT COMPLETE")
        print("=" * 60)
        
        return True

def main():
    """Run the deep generation audit"""
    auditor = DeepGenerationAuditor()
    auditor.run_full_audit()

if __name__ == "__main__":
    main()

