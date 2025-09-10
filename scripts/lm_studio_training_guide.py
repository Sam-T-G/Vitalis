#!/usr/bin/env python3
"""
LM Studio Emergency Relief AI Training Guide
Comprehensive setup and training workflow for GPT-OSS 20B emergency relief specialization
"""

import json
import requests
import time
import os
from pathlib import Path

class LMStudioTrainingGuide:
    """
    Complete guide for training emergency relief AI using LM Studio
    """
    
    def __init__(self):
        self.lm_studio_url = "http://localhost:1234"
        self.model_name = "gpt-oss-20b"
        self.training_data_path = "./data/ENHANCED_EMERGENCY_RELIEF_TRAINING_DATA.json"
        
    def step_1_verify_lm_studio(self):
        """Step 1: Verify LM Studio is running and accessible"""
        
        print("="*60)
        print("STEP 1: VERIFY LM STUDIO SETUP")
        print("="*60)
        
        # Check if LM Studio is running
        try:
            response = requests.get(f"{self.lm_studio_url}/v1/models", timeout=5)
            if response.status_code == 200:
                print("COMPLETED LM Studio is running and accessible")
                models = response.json()
                print(f"   Available models: {len(models.get('data', []))}")
                return True
            else:
                print("FAILED LM Studio is not responding correctly")
                return False
        except requests.exceptions.RequestException:
            print("FAILED Cannot connect to LM Studio")
            print("\nCONFIG MANUAL STEPS REQUIRED:")
            print("   1. Open LM Studio application")
            print("   2. Go to 'Local Server' tab")
            print("   3. Start the server on port 1234")
            print("   4. Load GPT-OSS 20B model")
            return False
    
    def step_2_load_model(self):
        """Step 2: Load GPT-OSS 20B model in LM Studio"""
        
        print("\n" + "="*60)
        print("STEP 2: LOAD GPT-OSS 20B MODEL")
        print("="*60)
        
        print("CONFIG MANUAL STEPS REQUIRED:")
        print("   1. In LM Studio, go to 'Chat' tab")
        print("   2. Click 'Select a model to load'")
        print("   3. Find and select 'gpt-oss-20b' from your local models")
        print("   4. Wait for model to load (may take 2-3 minutes)")
        print("   5. Test with a simple prompt like 'Hello'")
        
        input("\n   Press Enter when model is loaded and tested...")
        
        # Verify model is loaded
        try:
            response = requests.post(f"{self.lm_studio_url}/v1/chat/completions", 
                json={
                    "model": "gpt-oss-20b",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                }, timeout=30)
            
            if response.status_code == 200:
                print("COMPLETED Model loaded and responding correctly")
                return True
            else:
                print("FAILED Model not responding correctly")
                return False
        except requests.exceptions.RequestException:
            print("FAILED Cannot connect to model")
            return False
    
    def step_3_prepare_training_data(self):
        """Step 3: Prepare and validate training data"""
        
        print("\n" + "="*60)
        print("STEP 3: PREPARE TRAINING DATA")
        print("="*60)
        
        # Load and validate training data
        try:
            with open(self.training_data_path, 'r') as f:
                data = json.load(f)
            
            training_examples = data.get('training_data', [])
            print(f"COMPLETED Training data loaded: {len(training_examples)} examples")
            
            # Validate data structure
            required_keys = ['instruction', 'response']
            valid_examples = 0
            
            for example in training_examples[:5]:  # Check first 5
                if all(key in example for key in required_keys):
                    valid_examples += 1
            
            if valid_examples == 5:
                print("COMPLETED Training data format is valid")
                
                # Show sample
                sample = training_examples[0]
                print("\nCHECKLIST Sample Training Example:")
                print(f"   Instruction: {sample['instruction'][:100]}...")
                print(f"   Response: {sample['response'][:100]}...")
                
                return True
            else:
                print("FAILED Training data format issues detected")
                return False
                
        except FileNotFoundError:
            print(f"FAILED Training data file not found: {self.training_data_path}")
            return False
        except json.JSONDecodeError:
            print("FAILED Training data is not valid JSON")
            return False
    
    def step_4_lm_studio_training_setup(self):
        """Step 4: Set up fine-tuning in LM Studio"""
        
        print("\n" + "="*60)
        print("STEP 4: LM STUDIO FINE-TUNING SETUP")
        print("="*60)
        
        print("CONFIG MANUAL STEPS REQUIRED:")
        print("   1. In LM Studio, go to 'Developer' tab")
        print("   2. Look for 'Fine-tuning' or 'Training' section")
        print("   3. If not available, check LM Studio settings for beta features")
        print("   4. Enable fine-tuning features if needed")
        
        print("\nCHECKLIST TRAINING CONFIGURATION:")
        print("   Base Model: gpt-oss-20b")
        print("   Training Data: ENHANCED_EMERGENCY_RELIEF_TRAINING_DATA.json")
        print("   Learning Rate: 0.0001 (conservative)")
        print("   Batch Size: 2-4 (optimal for M4 MacBook Pro)")
        print("   Epochs: 3-5 (sufficient for specialization)")
        print("   Context Length: 2048 tokens")
        
        print("\nSETTINGS RECOMMENDED SETTINGS:")
        print("   - Enable gradient checkpointing")
        print("   - Use mixed precision (FP16/BF16)")
        print("   - Save checkpoints every 100 steps")
        print("   - Monitor training loss")
        
        input("\n   Press Enter when ready to proceed...")
        return True
    
    def step_5_alternative_training_approach(self):
        """Step 5: Alternative training approach using JSONL format"""
        
        print("\n" + "="*60)
        print("STEP 5: ALTERNATIVE TRAINING APPROACH")
        print("="*60)
        
        # Convert training data to JSONL format for LM Studio
        jsonl_path = "./data/emergency_relief_training.jsonl"
        
        try:
            with open(self.training_data_path, 'r') as f:
                data = json.load(f)
            
            training_examples = data.get('training_data', [])
            
            # Convert to JSONL format
            with open(jsonl_path, 'w') as f:
                for example in training_examples:
                    # Format for chat completion training
                    training_item = {
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert emergency relief coordinator. Provide detailed, actionable guidance for disaster response, resource coordination, and emergency management. Always prioritize safety and follow established protocols."
                            },
                            {
                                "role": "user", 
                                "content": example.get('instruction', '')
                            },
                            {
                                "role": "assistant",
                                "content": example.get('response', '')
                            }
                        ]
                    }
                    f.write(json.dumps(training_item) + '\n')
            
            print(f"COMPLETED Created JSONL training file: {jsonl_path}")
            print(f"   Contains {len(training_examples)} training conversations")
            
            print("\nCONFIG USE THIS FILE IN LM STUDIO:")
            print(f"   File path: {os.path.abspath(jsonl_path)}")
            print("   Format: Chat completion JSONL")
            print("   Purpose: Emergency relief AI specialization")
            
            return True
            
        except Exception as e:
            print(f"FAILED Failed to create JSONL file: {str(e)}")
            return False
    
    def step_6_monitor_training(self):
        """Step 6: Training monitoring and validation"""
        
        print("\n" + "="*60)
        print("STEP 6: TRAINING MONITORING")
        print("="*60)
        
        print("METRICS WHAT TO MONITOR DURING TRAINING:")
        print("   - Training loss (should decrease steadily)")
        print("   - Memory usage (keep under 20GB on M4 MacBook Pro)")
        print("   - Temperature (ensure MacBook stays cool)")
        print("   - Training time (expect 2-4 hours total)")
        
        print("\nTARGET SUCCESS INDICATORS:")
        print("   - Loss decreases from ~2.0 to ~0.5")
        print("   - No memory overflow errors")
        print("   - Model responds coherently to emergency prompts")
        print("   - Training completes without crashes")
        
        print("\nWARNING WARNING SIGNS:")
        print("   - Loss increases or plateaus early")
        print("   - Out of memory errors")
        print("   - MacBook overheating")
        print("   - Model outputs become nonsensical")
        
        return True
    
    def step_7_test_trained_model(self):
        """Step 7: Test the fine-tuned model"""
        
        print("\n" + "="*60)
        print("STEP 7: TEST FINE-TUNED MODEL")
        print("="*60)
        
        test_prompts = [
            "How do you coordinate evacuation during a wildfire?",
            "What are the essential supplies for emergency shelter setup?",
            "How do you manage volunteers during disaster response?",
            "What are the steps for medical triage in mass casualties?",
            "How do you establish communication protocols during a disaster?"
        ]
        
        print("TEST TEST PROMPTS FOR VALIDATION:")
        for i, prompt in enumerate(test_prompts, 1):
            print(f"   {i}. {prompt}")
        
        print("\nCONFIG MANUAL TESTING STEPS:")
        print("   1. In LM Studio, load your fine-tuned model")
        print("   2. Test each prompt above")
        print("   3. Verify responses are:")
        print("      - Accurate and professional")
        print("      - Specific to emergency relief")
        print("      - Actionable and clear")
        print("      - Safety-focused")
        
        print("\nCOMPLETED SUCCESS CRITERIA:")
        print("   - Responses demonstrate emergency relief expertise")
        print("   - Clear improvement over base model")
        print("   - Consistent professional tone")
        print("   - Accurate procedural guidance")
        
        return True
    
    def run_complete_guide(self):
        """Run the complete training guide"""
        
        print("LAUNCH LM STUDIO EMERGENCY RELIEF AI TRAINING GUIDE")
        print("=" * 60)
        print("This guide will walk you through training GPT-OSS 20B")
        print("for emergency relief specialization using LM Studio")
        print("=" * 60)
        
        steps = [
            self.step_1_verify_lm_studio,
            self.step_2_load_model,
            self.step_3_prepare_training_data,
            self.step_4_lm_studio_training_setup,
            self.step_5_alternative_training_approach,
            self.step_6_monitor_training,
            self.step_7_test_trained_model
        ]
        
        for i, step in enumerate(steps, 1):
            success = step()
            if not success:
                print(f"\nFAILED Step {i} failed. Please resolve issues before continuing.")
                return False
            
            if i < len(steps):
                input(f"\n   COMPLETED Step {i} complete. Press Enter to continue to step {i+1}...")
        
        print("\n" + "="*60)
        print("SUCCESS TRAINING SETUP COMPLETE!")
        print("="*60)
        print("You now have everything ready to train your emergency relief AI.")
        print("Follow the LM Studio interface to start the fine-tuning process.")
        print("\nExpected training time: 2-4 hours on M4 MacBook Pro")
        print("=" * 60)
        
        return True

if __name__ == "__main__":
    guide = LMStudioTrainingGuide()
    guide.run_complete_guide()
