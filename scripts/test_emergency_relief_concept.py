#!/usr/bin/env python3
"""
Emergency Relief AI Concept Testing
Test the emergency relief capabilities using the base model with specialized prompting
This demonstrates the concept without requiring fine-tuning
"""

import os
import json
import torch
import time
from transformers import AutoTokenizer, AutoModelForCausalLM
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)

class EmergencyReliefConceptTester:
    """
    Test emergency relief AI concept using base model + specialized prompting
    """
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        
        # Emergency relief system prompt
        self.system_prompt = """You are an expert emergency relief coordinator with extensive experience in disaster response, resource coordination, and emergency management. You follow established protocols from FEMA, WHO, Red Cross, and international standards.

Your responses should be:
- Detailed and actionable with step-by-step procedures
- Safety-focused and risk-aware
- Professional and authoritative
- Based on established emergency management protocols
- Clear and easy to follow under stress

Always prioritize safety and human life in your guidance."""

        # Test scenarios from your enhanced training data
        self.test_scenarios = [
            "How do you coordinate evacuation during a wildfire threatening a residential area?",
            "What are the essential supplies and setup procedures for an emergency shelter?",
            "How do you manage and coordinate volunteers during a disaster response operation?",
            "What are the steps for medical triage in a mass casualty incident?",
            "How do you establish communication protocols during a disaster when normal systems are down?",
            "What is the protocol for international disaster relief coordination?",
            "How do you assess infrastructure damage after an earthquake?",
            "What are the public health priorities during a pandemic emergency response?"
        ]
    
    def load_model(self) -> bool:
        """Load model with conservative settings"""
        try:
            print("PROCESSING Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                local_files_only=True,
                trust_remote_code=True
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            print("COMPLETED Tokenizer loaded")
            
            print("PROCESSING Loading model (this may take a few minutes)...")
            print("   Using conservative settings to avoid memory issues...")
            
            # Load with bfloat16 for Apple Silicon consistency
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                local_files_only=True,
                trust_remote_code=True,
                device_map="cpu",
                torch_dtype=torch.bfloat16,  # Apple Silicon native
                low_cpu_mem_usage=True
            )
            
            # Ensure dtype consistency
            self.model = self.model.to(dtype=torch.bfloat16)
            print(f"COMPLETED Model loaded with consistent bfloat16 dtype")
            
            print("COMPLETED Model loaded successfully on CPU")
            return True
            
        except Exception as e:
            print(f"FAILED Model loading failed: {e}")
            return False
    
    def generate_emergency_response(self, scenario: str) -> str:
        """Generate emergency relief guidance for a scenario"""
        try:
            # Create conversation with emergency relief context
            conversation = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": scenario}
            ]
            
            # Format using chat template
            formatted_prompt = self.tokenizer.apply_chat_template(
                conversation,
                tokenize=False,
                add_generation_prompt=True
            )
            
            print(f"SEARCH Generating response for: {scenario[:60]}...")
            
            # Tokenize
            inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
            
            # Generate with conservative settings
            start_time = time.time()
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_new_tokens=200,  # Moderate length
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1
                )
            
            generation_time = time.time() - start_time
            
            # Decode response
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response_only = full_response[len(formatted_prompt):].strip()
            
            print(f"COMPLETED Response generated in {generation_time:.1f}s")
            return response_only
            
        except Exception as e:
            print(f"FAILED Generation failed: {e}")
            return f"Error generating response: {str(e)}"
    
    def evaluate_emergency_capabilities(self):
        """Evaluate the base model's emergency relief capabilities"""
        print("TEST EMERGENCY RELIEF AI CONCEPT EVALUATION")
        print("=" * 60)
        print("Testing base GPT-OSS 20B model with emergency relief prompting")
        print("This demonstrates the potential without fine-tuning")
        print("=" * 60)
        
        if not self.load_model():
            print("FAILED Cannot proceed - model loading failed")
            return False
        
        print(f"\nCHECKLIST Testing {len(self.test_scenarios)} emergency scenarios:")
        print("-" * 60)
        
        results = []
        
        for i, scenario in enumerate(self.test_scenarios, 1):
            print(f"\n{i}. SCENARIO: {scenario}")
            print("-" * 40)
            
            response = self.generate_emergency_response(scenario)
            
            print(f"RESPONSE:\n{response}")
            print("-" * 60)
            
            # Basic evaluation
            is_emergency_focused = any(word in response.lower() for word in 
                                     ['emergency', 'safety', 'evacuation', 'disaster', 'rescue', 'relief'])
            is_actionable = any(word in response.lower() for word in 
                              ['step', 'procedure', 'process', 'action', 'establish', 'coordinate'])
            
            results.append({
                'scenario': scenario,
                'response': response,
                'emergency_focused': is_emergency_focused,
                'actionable': is_actionable,
                'response_length': len(response)
            })
            
            print(f"METRICS Quality Assessment:")
            print(f"   Emergency-focused: {'COMPLETED' if is_emergency_focused else 'FAILED'}")
            print(f"   Actionable guidance: {'COMPLETED' if is_actionable else 'FAILED'}")
            print(f"   Response length: {len(response)} characters")
        
        # Summary
        emergency_focused_count = sum(1 for r in results if r['emergency_focused'])
        actionable_count = sum(1 for r in results if r['actionable'])
        avg_length = sum(r['response_length'] for r in results) / len(results)
        
        print("\n" + "=" * 60)
        print("METRICS EVALUATION SUMMARY")
        print("=" * 60)
        print(f"Scenarios tested: {len(results)}")
        print(f"Emergency-focused responses: {emergency_focused_count}/{len(results)} ({emergency_focused_count/len(results)*100:.1f}%)")
        print(f"Actionable guidance: {actionable_count}/{len(results)} ({actionable_count/len(results)*100:.1f}%)")
        print(f"Average response length: {avg_length:.0f} characters")
        
        # Overall assessment
        if emergency_focused_count >= len(results) * 0.8 and actionable_count >= len(results) * 0.7:
            print("\nSUCCESS EXCELLENT: Base model shows strong emergency relief capabilities!")
            print("   COMPLETED Fine-tuning would likely produce exceptional results")
            print("   COMPLETED The concept is validated and ready for optimization")
        elif emergency_focused_count >= len(results) * 0.6:
            print("\nCOMPLETED GOOD: Base model shows promise for emergency relief")
            print("   CONFIG Fine-tuning would significantly improve performance")
            print("   IDEA Consider expanding training data for better coverage")
        else:
            print("\nWARNING FAIR: Base model needs significant improvement")
            print("   CONFIG Fine-tuning is essential for emergency relief use")
            print("   LIBRARY More comprehensive training data recommended")
        
        return True

def main():
    """Main testing function"""
    model_path = "./models/gpt-oss-20b"
    
    if not os.path.exists(model_path):
        print(f"FAILED Model not found at: {model_path}")
        return 1
    
    print("LAUNCH EMERGENCY RELIEF AI CONCEPT TESTING")
    print("Testing the base model's emergency relief capabilities")
    print("This validates our approach before fine-tuning optimization")
    print("\nWARNING Note: This will load the model on CPU (may be slow but stable)")
    
    response = input("\nContinue with concept testing? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("FAILED Testing cancelled")
        return 0
    
    tester = EmergencyReliefConceptTester(model_path)
    success = tester.evaluate_emergency_capabilities()
    
    if success:
        print("\nTARGET CONCEPT VALIDATION COMPLETE!")
        print("This demonstrates the potential of your emergency relief AI.")
        print("Next steps would be optimizing the fine-tuning approach.")
        return 0
    else:
        return 1

if __name__ == "__main__":
    exit(main())
