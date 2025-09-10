#!/usr/bin/env python3
"""
Emergency Relief AI Model Testing Script
Comprehensive testing of the fine-tuned emergency relief model
"""

import sys
import os
import json
import torch
import time
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EmergencyReliefModelTester:
    """
    Comprehensive testing class for the emergency relief model
    """
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        
        # Test scenarios organized by category
        self.test_scenarios = {
            "disaster_response": [
                "How do you coordinate evacuation during a wildfire?",
                "What are the first steps when responding to an earthquake?",
                "How do you establish incident command during a hurricane?"
            ],
            "shelter_management": [
                "What are the essential supplies for emergency shelter setup?",
                "How do you manage overcrowding in emergency shelters?",
                "What protocols ensure safety in temporary shelters?"
            ],
            "resource_coordination": [
                "How do you allocate limited medical supplies during a disaster?",
                "What's the process for coordinating food distribution?",
                "How do you track and manage donated resources?"
            ],
            "volunteer_management": [
                "How do you manage volunteers during disaster response?",
                "What training do emergency volunteers need?",
                "How do you coordinate volunteer deployment?"
            ],
            "medical_emergency": [
                "What are the steps for medical triage in mass casualties?",
                "How do you set up a field medical station?",
                "What's the protocol for handling infectious disease outbreaks?"
            ],
            "communication_protocols": [
                "How do you establish communication protocols during a disaster?",
                "What backup communication systems should be in place?",
                "How do you coordinate information between agencies?"
            ]
        }
    
    def load_model(self) -> bool:
        """Load the fine-tuned model"""
        try:
            logging.info(f"Loading model from {self.model_path}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                local_files_only=True,
                trust_remote_code=True
            )
            
            # Load model with fallback strategies
            strategies = [
                {"device_map": "auto", "torch_dtype": torch.bfloat16},
                {"device_map": "cpu", "torch_dtype": torch.bfloat16},
                {"device_map": "auto", "torch_dtype": torch.float32}
            ]
            
            for strategy in strategies:
                try:
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_path,
                        local_files_only=True,
                        trust_remote_code=True,
                        low_cpu_mem_usage=True,
                        **strategy
                    )
                    logging.info(f"COMPLETED Model loaded successfully")
                    return True
                except Exception as e:
                    logging.warning(f"Strategy failed: {e}")
                    continue
            
            logging.error("FAILED All loading strategies failed")
            return False
            
        except Exception as e:
            logging.error(f"FAILED Failed to load model: {e}")
            return False
    
    def generate_response(self, prompt: str, max_tokens: int = 200) -> str:
        """Generate response for a given prompt"""
        try:
            # Create conversation format
            conversation = [
                {
                    "role": "system", 
                    "content": "You are an expert emergency relief coordinator. Provide detailed, actionable guidance for disaster response, resource coordination, and emergency management. Always prioritize safety and follow established protocols."
                },
                {"role": "user", "content": prompt}
            ]
            
            # Apply chat template
            formatted_prompt = self.tokenizer.apply_chat_template(
                conversation,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # Tokenize
            inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
            
            # Generate
            start_time = time.time()
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_new_tokens=max_tokens,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1
                )
            
            generation_time = time.time() - start_time
            
            # Decode response
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response_only = full_response[len(formatted_prompt):].strip()
            
            return response_only, generation_time
            
        except Exception as e:
            logging.error(f"FAILED Failed to generate response: {e}")
            return f"Error: {str(e)}", 0
    
    def test_category(self, category: str, scenarios: list) -> dict:
        """Test all scenarios in a category"""
        logging.info(f"Testing category: {category.upper()}")
        
        results = {
            "category": category,
            "total_scenarios": len(scenarios),
            "responses": [],
            "avg_response_time": 0,
            "success_count": 0
        }
        
        total_time = 0
        
        for i, scenario in enumerate(scenarios, 1):
            logging.info(f"  Scenario {i}/{len(scenarios)}: {scenario}")
            
            response, response_time = self.generate_response(scenario)
            total_time += response_time
            
            if not response.startswith("Error:"):
                results["success_count"] += 1
            
            results["responses"].append({
                "scenario": scenario,
                "response": response,
                "response_time": response_time,
                "success": not response.startswith("Error:")
            })
            
            # Print response (truncated)
            print(f"    Response: {response[:150]}...")
            print(f"    Time: {response_time:.2f}s")
            print("-" * 60)
        
        results["avg_response_time"] = total_time / len(scenarios)
        
        return results
    
    def run_comprehensive_test(self) -> dict:
        """Run comprehensive testing across all categories"""
        logging.info("TEST STARTING COMPREHENSIVE MODEL TESTING")
        logging.info("=" * 60)
        
        if not self.load_model():
            return {"error": "Failed to load model"}
        
        all_results = {
            "model_path": self.model_path,
            "test_timestamp": time.time(),
            "categories": {},
            "summary": {}
        }
        
        total_scenarios = 0
        total_successes = 0
        total_time = 0
        
        # Test each category
        for category, scenarios in self.test_scenarios.items():
            results = self.test_category(category, scenarios)
            all_results["categories"][category] = results
            
            total_scenarios += results["total_scenarios"]
            total_successes += results["success_count"]
            total_time += results["avg_response_time"] * results["total_scenarios"]
        
        # Calculate summary statistics
        all_results["summary"] = {
            "total_scenarios": total_scenarios,
            "total_successes": total_successes,
            "success_rate": (total_successes / total_scenarios) * 100 if total_scenarios > 0 else 0,
            "avg_response_time": total_time / total_scenarios if total_scenarios > 0 else 0,
            "categories_tested": len(self.test_scenarios)
        }
        
        return all_results
    
    def save_results(self, results: dict, output_path: str):
        """Save test results to file"""
        try:
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            logging.info(f"COMPLETED Results saved to {output_path}")
        except Exception as e:
            logging.error(f"FAILED Failed to save results: {e}")
    
    def print_summary(self, results: dict):
        """Print a summary of test results"""
        if "error" in results:
            print(f"FAILED Testing failed: {results['error']}")
            return
        
        summary = results["summary"]
        
        print("\n" + "=" * 60)
        print("METRICS EMERGENCY RELIEF AI TEST SUMMARY")
        print("=" * 60)
        print(f"TARGET Model: {results['model_path']}")
        print(f"CHECKLIST Total scenarios tested: {summary['total_scenarios']}")
        print(f"COMPLETED Successful responses: {summary['total_successes']}")
        print(f"PROGRESS Success rate: {summary['success_rate']:.1f}%")
        print(f"TIME  Average response time: {summary['avg_response_time']:.2f}s")
        print(f" Categories tested: {summary['categories_tested']}")
        
        print("\nMETRICS CATEGORY BREAKDOWN:")
        for category, data in results["categories"].items():
            success_rate = (data["success_count"] / data["total_scenarios"]) * 100
            print(f"  {category}: {data['success_count']}/{data['total_scenarios']} ({success_rate:.1f}%) - {data['avg_response_time']:.2f}s avg")
        
        print("\n" + "=" * 60)
        
        # Quality assessment
        if summary['success_rate'] >= 90:
            print("SUCCESS EXCELLENT: Model performs excellently on emergency scenarios!")
        elif summary['success_rate'] >= 75:
            print("COMPLETED GOOD: Model performs well with minor issues")
        elif summary['success_rate'] >= 50:
            print("WARNING  FAIR: Model has some issues, consider additional training")
        else:
            print("FAILED POOR: Model needs significant improvement")

def main():
    """Main testing function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Emergency Relief AI Model")
    parser.add_argument(
        "--model-path", 
        default="./models/emergency_relief_fine_tuned/emergency_relief_model",
        help="Path to the fine-tuned model"
    )
    parser.add_argument(
        "--output", 
        default="./test_results.json",
        help="Output file for test results"
    )
    
    args = parser.parse_args()
    
    # Check if model exists
    if not os.path.exists(args.model_path):
        print(f"FAILED Model not found at: {args.model_path}")
        print("IDEA Make sure to train the model first using train_emergency_relief_ai.py")
        return 1
    
    # Run tests
    tester = EmergencyReliefModelTester(args.model_path)
    results = tester.run_comprehensive_test()
    
    # Save and display results
    tester.save_results(results, args.output)
    tester.print_summary(results)
    
    # Return appropriate exit code
    if "error" in results:
        return 1
    elif results["summary"]["success_rate"] >= 75:
        return 0
    else:
        return 1

if __name__ == "__main__":
    exit(main())
