#!/usr/bin/env python3
"""
GPT-OSS Harmony Format Test
Test the model with proper harmony response format as required by GPT-OSS
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import warnings
import time
import threading
import queue
warnings.filterwarnings("ignore")

class HarmonyFormatTester:
    """Test GPT-OSS with proper harmony format"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.loaded = False
    
    def load_model_fast(self):
        """Load model with minimal configuration for testing"""
        print("Loading GPT-OSS model for harmony format testing...")
        
        try:
            base_model_path = "./models/gpt-oss-20b"
            lora_model_path = "./models/emergency_relief_fine_tuned/emergency_relief_lora"
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                base_model_path,
                local_files_only=True,
                trust_remote_code=True
            )
            
            # Configure tokenizer properly
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = "<|endoftext|>"
                self.tokenizer.pad_token_id = 199999
            self.tokenizer.padding_side = "left"
            
            # Load base model
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_path,
                local_files_only=True,
                trust_remote_code=True,
                device_map="cpu",
                torch_dtype=torch.bfloat16,
                low_cpu_mem_usage=True
            )
            
            # Load with LoRA
            self.model = PeftModel.from_pretrained(
                base_model,
                lora_model_path,
                torch_dtype=torch.bfloat16
            )
            
            self.model.eval()
            self.loaded = True
            print("Model loaded successfully!")
            return True
            
        except Exception as e:
            print(f"Model loading failed: {e}")
            return False
    
    def test_harmony_format(self):
        """Test with proper GPT-OSS harmony response format"""
        print("\n" + "=" * 60)
        print("TESTING HARMONY RESPONSE FORMAT")
        print("=" * 60)
        
        if not self.loaded:
            print("Model not loaded")
            return False
        
        # GPT-OSS harmony format with proper structure
        test_scenarios = [
            {
                "name": "Basic Harmony Format",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are ChatGPT, a large language model trained by OpenAI.\nKnowledge cutoff: 2024-06\nCurrent date: 2025-09-10\n\nReasoning: medium\n\n# Valid channels: analysis, commentary, final. Channel must be included for every message."
                    },
                    {
                        "role": "user",
                        "content": "What are the first steps for wildfire evacuation?"
                    }
                ]
            },
            {
                "name": "Emergency Relief with Harmony",
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are ChatGPT, a large language model trained by OpenAI.\nKnowledge cutoff: 2024-06\nCurrent date: 2025-09-10\n\nReasoning: high\n\nYou are an expert Emergency Relief Coordinator. Provide clear, actionable guidance for emergency situations.\n\n# Valid channels: analysis, commentary, final. Channel must be included for every message."
                    },
                    {
                        "role": "user",
                        "content": "Emergency: Wildfire approaching town. 2 hours to evacuate 500 people. What immediate steps?"
                    }
                ]
            },
            {
                "name": "Minimal Test",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are ChatGPT, a large language model trained by OpenAI.\nKnowledge cutoff: 2024-06\nCurrent date: 2025-09-10\n\nReasoning: low\n\n# Valid channels: analysis, commentary, final. Channel must be included for every message."
                    },
                    {
                        "role": "user",
                        "content": "Hello"
                    }
                ]
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\nTesting: {scenario['name']}")
            
            try:
                # Use the model's chat template
                prompt = self.tokenizer.apply_chat_template(
                    scenario['messages'],
                    tokenize=False,
                    add_generation_prompt=True
                )
                
                print(f"Generated prompt preview:")
                print(f"{prompt[:200]}...")
                
                # Tokenize
                inputs = self.tokenizer(
                    prompt,
                    return_tensors="pt",
                    truncation=True,
                    max_length=2048
                )
                
                print(f"Input length: {inputs.input_ids.shape[1]} tokens")
                
                # Test generation with timeout
                start_time = time.time()
                
                result_queue = queue.Queue()
                
                def generate_worker():
                    try:
                        with torch.no_grad():
                            outputs = self.model.generate(
                                inputs.input_ids,
                                attention_mask=inputs.get('attention_mask', None),
                                max_new_tokens=50,  # Start small
                                min_new_tokens=5,
                                temperature=0.3,
                                do_sample=True,
                                top_p=0.9,
                                pad_token_id=self.tokenizer.pad_token_id,
                                eos_token_id=[200002, 199999, 200012],
                                use_cache=True,
                                early_stopping=True
                            )
                        result_queue.put(('success', outputs))
                    except Exception as e:
                        result_queue.put(('error', str(e)))
                
                thread = threading.Thread(target=generate_worker)
                thread.daemon = True
                thread.start()
                thread.join(timeout=30)  # 30 second timeout
                
                generation_time = time.time() - start_time
                
                if thread.is_alive():
                    print(f"   TIMEOUT after 30s - Harmony format not fixing the issue")
                else:
                    try:
                        result_type, result = result_queue.get_nowait()
                        if result_type == 'success':
                            generated_text = self.tokenizer.decode(result[0], skip_special_tokens=True)
                            response = generated_text[len(prompt):].strip()
                            
                            # Clean response
                            for token in ["<|return|>", "<|endoftext|>", "<|call|>"]:
                                response = response.replace(token, "")
                            response = response.strip()
                            
                            print(f"   SUCCESS in {generation_time:.1f}s")
                            print(f"   Response: {response[:100]}{'...' if len(response) > 100 else ''}")
                            return True
                        else:
                            print(f"   Generation error: {result}")
                    except queue.Empty:
                        print(f"   No result returned")
                        
            except Exception as e:
                print(f"   Test failed: {e}")
        
        return False
    
    def test_without_lora(self):
        """Test base model without LoRA to isolate issues"""
        print("\n" + "=" * 60)
        print("TESTING BASE MODEL WITHOUT LORA")
        print("=" * 60)
        
        try:
            base_model_path = "./models/gpt-oss-20b"
            
            # Load just the base model
            print("Loading base model without LoRA...")
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_path,
                local_files_only=True,
                trust_remote_code=True,
                device_map="cpu",
                torch_dtype=torch.bfloat16,
                low_cpu_mem_usage=True
            )
            
            base_model.eval()
            
            # Simple test
            test_input = "Hello, how are you?"
            inputs = self.tokenizer(test_input, return_tensors="pt")
            
            print(f"Testing base model with: '{test_input}'")
            
            start_time = time.time()
            
            result_queue = queue.Queue()
            
            def generate_worker():
                try:
                    with torch.no_grad():
                        outputs = base_model.generate(
                            inputs.input_ids,
                            max_new_tokens=10,
                            do_sample=False,
                            pad_token_id=199999,
                            eos_token_id=200002,
                            use_cache=True
                        )
                    result_queue.put(('success', outputs))
                except Exception as e:
                    result_queue.put(('error', str(e)))
            
            thread = threading.Thread(target=generate_worker)
            thread.daemon = True
            thread.start()
            thread.join(timeout=20)
            
            generation_time = time.time() - start_time
            
            if thread.is_alive():
                print(f"   Base model also times out - Core model issue")
                return False
            else:
                try:
                    result_type, result = result_queue.get_nowait()
                    if result_type == 'success':
                        generated_text = self.tokenizer.decode(result[0], skip_special_tokens=True)
                        response = generated_text[len(test_input):].strip()
                        print(f"   Base model works in {generation_time:.1f}s")
                        print(f"   Response: '{response}'")
                        print("   Issue is likely with LoRA adapter or prompt format")
                        return True
                    else:
                        print(f"   Base model error: {result}")
                        return False
                except queue.Empty:
                    print(f"   No result from base model")
                    return False
                    
        except Exception as e:
            print(f"Base model test failed: {e}")
            return False
    
    def run_targeted_audit(self):
        """Run targeted audit focusing on harmony format and LoRA issues"""
        print("TARGETED GENERATION AUDIT")
        print("Testing specific hypotheses about timeout causes")
        print("=" * 60)
        
        # First test: Load model
        if not self.load_model_fast():
            print("Cannot load model")
            return False
        
        # Second test: Try harmony format
        print("\n1. Testing Harmony Response Format...")
        harmony_works = self.test_harmony_format()
        
        # Third test: Test without LoRA
        print("\n2. Testing Base Model Without LoRA...")
        base_works = self.test_without_lora()
        
        # Analysis
        print("\n" + "=" * 60)
        print("AUDIT RESULTS ANALYSIS")
        print("=" * 60)
        
        if harmony_works:
            print("SOLUTION FOUND: Harmony response format fixes the issue!")
            print("   Recommendation: Use proper GPT-OSS harmony format for all prompts")
        elif base_works and not harmony_works:
            print("ISSUE IDENTIFIED: LoRA adapter or prompt format problem")
            print("   Recommendation: Check LoRA compatibility or use base model")
        elif not base_works:
            print("CRITICAL ISSUE: Base model itself has problems")
            print("   Recommendation: Model configuration or environment issue")
        else:
            print("PARTIAL SUCCESS: Need further investigation")
        
        return harmony_works or base_works

def main():
    """Run the targeted audit"""
    tester = HarmonyFormatTester()
    tester.run_targeted_audit()

if __name__ == "__main__":
    main()
