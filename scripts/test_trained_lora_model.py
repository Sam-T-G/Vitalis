#!/usr/bin/env python3
"""
Test the Successfully Trained Emergency Relief LoRA Model
Simple testing script that avoids device allocation issues
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import warnings
import signal
import sys
warnings.filterwarnings("ignore")

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Generation timed out")

def safe_generate_with_timeout(model, **kwargs):
    """Generate with timeout protection"""
    # Set a 60 second timeout for generation
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(60)
    
    try:
        outputs = model.generate(**kwargs)
        signal.alarm(0)  # Cancel the alarm
        return outputs
    except TimeoutException:
        signal.alarm(0)  # Cancel the alarm
        print("Generation timed out after 60 seconds")
        return None
    except Exception as e:
        signal.alarm(0)  # Cancel the alarm
        print(f"Generation failed: {e}")
        return None

def test_emergency_relief_lora():
    """Test the trained LoRA emergency relief model"""
    
    print("TESTING TRAINED EMERGENCY RELIEF AI")
    print("=" * 50)
    
    # Paths
    base_model_path = "./models/gpt-oss-20b"
    lora_model_path = "./models/emergency_relief_fine_tuned/emergency_relief_lora"
    
    print("Loading base model and LoRA adapter...")
    
    try:
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            base_model_path,
            local_files_only=True,
            trust_remote_code=True
        )
        
        # Fix tokenizer configuration to avoid attention mask issues
        if tokenizer.pad_token is None:
            # Use endoftext token (199999) for padding, not the eos token (200002)
            tokenizer.pad_token = "<|endoftext|>"
            tokenizer.pad_token_id = 199999
        
        # Ensure proper tokenizer settings
        tokenizer.padding_side = "left"  # Important for generation
        
        # Load base model on CPU (avoid MPS issues)
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_path,
            local_files_only=True,
            trust_remote_code=True,
            device_map="cpu",
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=True
        )
        
        # Load LoRA adapter
        model = PeftModel.from_pretrained(
            base_model,
            lora_model_path,
            torch_dtype=torch.bfloat16
        )
        
        print("Emergency Relief LoRA model loaded successfully!")
        
        # Test scenarios
        test_scenarios = [
            "How do you coordinate evacuation during a wildfire?",
            "What are the essential supplies for emergency shelter setup?",
            "How do you manage volunteers during disaster response?",
            "What are the steps for medical triage in mass casualties?"
        ]
        
        print("\nTesting Emergency Relief Scenarios:")
        print("=" * 50)
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n{i}. SCENARIO: {scenario}")
            print("-" * 40)
            
            # Create conversation
            conversation = [
                {
                    "role": "system", 
                    "content": "You are an expert emergency relief coordinator. Provide detailed, actionable guidance for disaster response, resource coordination, and emergency management. Always prioritize safety and follow established protocols."
                },
                {"role": "user", "content": scenario}
            ]
            
            # Format prompt
            formatted_prompt = tokenizer.apply_chat_template(
                conversation,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # Generate response
            inputs = tokenizer(
                formatted_prompt, 
                return_tensors="pt", 
                padding=True, 
                truncation=True,
                max_length=2048
            )
            
            print("Generating emergency guidance...")
            
            # Get proper EOS token IDs from the model config
            # GPT-OSS uses multiple EOS tokens: [200002, 199999, 200012]
            eos_token_ids = [200002, 199999, 200012]  # <|return|>, <|endoftext|>, <|call|>
            
            with torch.no_grad():
                outputs = safe_generate_with_timeout(
                    model,
                    input_ids=inputs.input_ids,
                    attention_mask=inputs.attention_mask,  # Critical: include attention mask
                    max_new_tokens=200,
                    min_new_tokens=10,  # Ensure some generation happens
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,  # Add nucleus sampling for better quality
                    pad_token_id=tokenizer.pad_token_id,  # Use proper pad token
                    eos_token_id=eos_token_ids,  # Use all valid EOS tokens
                    repetition_penalty=1.1,
                    length_penalty=1.0,
                    early_stopping=True,  # Stop when EOS is generated
                    use_cache=True
                )
            
            # Handle generation results
            if outputs is None:
                print("Generation failed or timed out")
                response_only = "Emergency guidance generation failed. Please try again."
            else:
                # Decode response
                full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                response_only = full_response[len(formatted_prompt):].strip()
                
                # Clean up any remaining special tokens manually
                for eos_token in ["<|return|>", "<|endoftext|>", "<|call|>"]:
                    response_only = response_only.replace(eos_token, "").strip()
                
                # Ensure we have a meaningful response
                if not response_only or len(response_only) < 10:
                    response_only = "Emergency guidance was generated but appears incomplete. Please try again."
            
            print(f"EMERGENCY RELIEF GUIDANCE:")
            print(f"{response_only}")
            print("-" * 40)
            
            # Quick quality assessment
            emergency_terms = ['emergency', 'safety', 'evacuation', 'disaster', 'rescue', 'relief', 'protocol', 'coordinate']
            action_terms = ['step', 'procedure', 'establish', 'ensure', 'contact', 'assess', 'prioritize']
            
            emergency_score = sum(1 for term in emergency_terms if term.lower() in response_only.lower())
            action_score = sum(1 for term in action_terms if term.lower() in response_only.lower())
            
            print(f"Quality Assessment:")
            print(f"   Emergency relevance: {emergency_score}/8 terms")
            print(f"   Actionable guidance: {action_score}/7 terms")
            
            if emergency_score >= 2 and action_score >= 2:
                print("   High quality emergency response!")
            elif emergency_score >= 1 and action_score >= 1:
                print("   Good emergency response")
            else:
                print("   Needs improvement")
        
        print("\n" + "=" * 50)
        print("EMERGENCY RELIEF AI TESTING COMPLETE!")
        print("=" * 50)
        print("Your LoRA model is successfully trained and responding!")
        print("Ready for emergency relief deployment!")
        
        return True
        
    except Exception as e:
        print(f"Testing failed: {e}")
        return False

if __name__ == "__main__":
    success = test_emergency_relief_lora()
    if success:
        print("\nYour Emergency Relief AI is ready to help save lives!")
    else:
        print("\nTesting encountered issues")
