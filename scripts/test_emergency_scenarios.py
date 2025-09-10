#!/usr/bin/env python3
"""
Emergency Scenarios Testing Script
Test the Emergency Relief AI with realistic emergency situations
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from peft import PeftModel
import warnings
import time
import json
warnings.filterwarnings("ignore")

class EmergencyScenarioTester:
    """Test Emergency Relief AI with realistic scenarios"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.loaded = False
        
        # Realistic emergency scenarios
        self.emergency_scenarios = [
            {
                "category": "Wildfire Response",
                "scenario": "A fast-moving wildfire is approaching our residential area with 500 homes. Winds are gusting at 40 mph, and we have approximately 2 hours before the fire reaches the first houses. What immediate evacuation steps should we take?",
                "expected_elements": ["evacuation routes", "shelter locations", "communication", "transportation", "vulnerable populations"]
            },
            {
                "category": "Flood Emergency",
                "scenario": "Heavy rainfall has caused the main river to overflow. Downtown area is flooding with 4 feet of water. 150 people are stranded in buildings. Emergency services are stretched thin. How do we coordinate rescue operations?",
                "expected_elements": ["rescue prioritization", "boat deployment", "safety protocols", "communication", "medical support"]
            },
            {
                "category": "Earthquake Response",
                "scenario": "A 6.8 magnitude earthquake just struck our city. Multiple buildings have collapsed, power grid is down, and communication networks are failing. We have reports of people trapped in rubble. What's our immediate response protocol?",
                "expected_elements": ["search and rescue", "triage", "communication backup", "resource coordination", "safety assessment"]
            },
            {
                "category": "Mass Casualty Incident",
                "scenario": "A major traffic accident on the highway involves 3 vehicles with 12 people injured, including 4 with critical injuries. Local hospital is 20 minutes away and has limited trauma capacity. How do we handle triage and transport?",
                "expected_elements": ["triage protocols", "transport priorities", "medical care", "scene safety", "resource allocation"]
            },
            {
                "category": "Hurricane Preparation",
                "scenario": "A Category 4 hurricane will make landfall in 24 hours. Our coastal town has 8,000 residents, many elderly. Mandatory evacuation has been ordered for flood zones. How do we execute the evacuation plan?",
                "expected_elements": ["evacuation zones", "transportation", "shelter management", "vulnerable populations", "communication"]
            },
            {
                "category": "Chemical Spill",
                "scenario": "A tanker truck carrying hazardous chemicals has overturned on a major road near a school. Unknown chemical is leaking, and wind is blowing toward the residential area. 200 people need immediate evacuation. What are our steps?",
                "expected_elements": ["hazmat protocols", "evacuation perimeter", "decontamination", "medical monitoring", "air quality"]
            },
            {
                "category": "Winter Storm Response",
                "scenario": "A severe blizzard has dumped 3 feet of snow in 8 hours. Power is out for 15,000 residents, temperature is -10°F, and roads are impassable. Multiple people are calling for help with medical emergencies. How do we respond?",
                "expected_elements": ["warming centers", "emergency medical access", "power restoration", "welfare checks", "resource distribution"]
            },
            {
                "category": "Building Collapse",
                "scenario": "A 5-story apartment building has partially collapsed during construction work nearby. An estimated 30 people may be trapped inside. Structural engineers warn the remaining structure is unstable. How do we approach rescue operations?",
                "expected_elements": ["structural assessment", "search and rescue", "safety zones", "heavy equipment", "medical teams"]
            }
        ]
    
    def load_model(self):
        """Load the Emergency Relief AI model"""
        base_model_path = "./models/gpt-oss-20b"
        lora_model_path = "./models/emergency_relief_fine_tuned/emergency_relief_lora"
        
        print("EMERGENCY SCENARIOS TESTING")
        print("=" * 50)
        print("Loading Emergency Relief AI model...")
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                base_model_path,
                local_files_only=True,
                trust_remote_code=True
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = "<|endoftext|>"
                self.tokenizer.pad_token_id = 199999
            self.tokenizer.padding_side = "left"
            
            # Load models
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_path,
                local_files_only=True,
                trust_remote_code=True,
                device_map="cpu",
                torch_dtype=torch.bfloat16,
                low_cpu_mem_usage=True
            )
            
            self.model = PeftModel.from_pretrained(
                base_model,
                lora_model_path,
                torch_dtype=torch.bfloat16
            )
            
            self.generation_config = GenerationConfig(
                max_new_tokens=200,
                min_new_tokens=30,
                temperature=0.2,  # Lower temperature for more focused emergency responses
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.05,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=[200002, 199999],
                early_stopping=True,
                use_cache=True
            )
            
            print("Model loaded successfully!")
            self.loaded = True
            return True
            
        except Exception as e:
            print(f"Failed to load model: {e}")
            return False
    
    def test_scenario(self, scenario_data):
        """Test a single emergency scenario"""
        scenario = scenario_data["scenario"]
        category = scenario_data["category"]
        
        print(f"\nTesting: {category}")
        print("-" * 40)
        print(f"Scenario: {scenario}")
        print("\nGenerating emergency response...")
        
        try:
            # Create emergency response prompt
            conversation = [
                {
                    "role": "system",
                    "content": "You are an expert Emergency Relief Coordinator with 20 years of experience. Provide clear, actionable, step-by-step emergency response guidance. Focus on immediate actions, safety protocols, and resource coordination. Be specific and prioritize life safety."
                },
                {
                    "role": "user", 
                    "content": f"EMERGENCY SITUATION: {scenario}\n\nProvide immediate response guidance with specific action steps."
                }
            ]
            
            # Format prompt
            prompt = self.tokenizer.apply_chat_template(
                conversation,
                tokenize=False,
                add_generation_prompt=True
            )
            
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=1024
            )
            
            start_time = time.time()
            
            # Generate with timeout
            import threading
            import queue
            
            result_queue = queue.Queue()
            
            def generate_worker():
                try:
                    with torch.no_grad():
                        outputs = self.model.generate(
                            inputs.input_ids,
                            attention_mask=inputs.get('attention_mask', None),
                            generation_config=self.generation_config
                        )
                    result_queue.put(('success', outputs))
                except Exception as e:
                    result_queue.put(('error', str(e)))
            
            thread = threading.Thread(target=generate_worker)
            thread.daemon = True
            thread.start()
            thread.join(timeout=60)  # 60 second timeout
            
            if thread.is_alive():
                response = "Response generation timed out"
                quality_score = 0
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
                        
                        # Evaluate response quality
                        quality_score = self.evaluate_response(response, scenario_data)
                    else:
                        response = f"Generation error: {result}"
                        quality_score = 0
                except queue.Empty:
                    response = "Generation failed to complete"
                    quality_score = 0
            
            generation_time = time.time() - start_time
            
            print(f"\nEMERGENCY RESPONSE:")
            print("=" * 40)
            print(response)
            print("=" * 40)
            print(f"Generation Time: {generation_time:.1f}s")
            print(f"Response Quality Score: {quality_score}/10")
            
            return {
                "category": category,
                "scenario": scenario,
                "response": response,
                "quality_score": quality_score,
                "generation_time": generation_time
            }
            
        except Exception as e:
            print(f"Error testing scenario: {e}")
            return {
                "category": category,
                "scenario": scenario,
                "response": f"Error: {e}",
                "quality_score": 0,
                "generation_time": 0
            }
    
    def evaluate_response(self, response, scenario_data):
        """Evaluate the quality of the emergency response"""
        if not response or len(response) < 20:
            return 0
        
        score = 0
        response_lower = response.lower()
        
        # Check for emergency response elements
        emergency_terms = ['emergency', 'safety', 'evacuation', 'rescue', 'protocol', 'coordinate', 'assess', 'immediate']
        action_terms = ['step', 'first', 'next', 'ensure', 'establish', 'contact', 'deploy', 'activate']
        
        # Score based on emergency terminology (0-3 points)
        emergency_count = sum(1 for term in emergency_terms if term in response_lower)
        score += min(3, emergency_count)
        
        # Score based on actionable guidance (0-3 points)
        action_count = sum(1 for term in action_terms if term in response_lower)
        score += min(3, action_count)
        
        # Score based on expected elements for this scenario (0-3 points)
        expected_elements = scenario_data.get("expected_elements", [])
        element_count = sum(1 for element in expected_elements if element.lower() in response_lower)
        if expected_elements:
            element_score = (element_count / len(expected_elements)) * 3
            score += element_score
        
        # Score based on response length and structure (0-1 point)
        if len(response) > 100 and ('1.' in response or 'step' in response_lower):
            score += 1
        
        return min(10, round(score, 1))
    
    def run_all_scenarios(self):
        """Test all emergency scenarios"""
        if not self.load_model():
            return
        
        results = []
        total_scenarios = len(self.emergency_scenarios)
        
        print(f"\nTesting {total_scenarios} emergency scenarios...")
        print("=" * 50)
        
        for i, scenario in enumerate(self.emergency_scenarios, 1):
            print(f"\n[{i}/{total_scenarios}] {scenario['category']}")
            result = self.test_scenario(scenario)
            results.append(result)
            
            # Brief pause between scenarios
            time.sleep(2)
        
        # Generate summary report
        self.generate_summary_report(results)
        
        return results
    
    def generate_summary_report(self, results):
        """Generate a summary report of all test results"""
        print("\n" + "=" * 60)
        print("EMERGENCY SCENARIOS TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(results)
        total_score = sum(r['quality_score'] for r in results)
        avg_score = total_score / total_tests if total_tests > 0 else 0
        avg_time = sum(r['generation_time'] for r in results) / total_tests if total_tests > 0 else 0
        
        print(f"Total Scenarios Tested: {total_tests}")
        print(f"Average Quality Score: {avg_score:.1f}/10")
        print(f"Average Generation Time: {avg_time:.1f}s")
        print()
        
        # Score breakdown
        excellent = sum(1 for r in results if r['quality_score'] >= 8)
        good = sum(1 for r in results if 6 <= r['quality_score'] < 8)
        fair = sum(1 for r in results if 4 <= r['quality_score'] < 6)
        poor = sum(1 for r in results if r['quality_score'] < 4)
        
        print("Quality Distribution:")
        print(f"  Excellent (8-10): {excellent} scenarios")
        print(f"  Good (6-7):       {good} scenarios")
        print(f"  Fair (4-5):       {fair} scenarios")
        print(f"  Poor (0-3):       {poor} scenarios")
        
        print("\nDetailed Results:")
        print("-" * 60)
        for result in results:
            print(f"{result['category']:<25} Score: {result['quality_score']}/10")
        
        print("=" * 60)
        
        # Overall assessment
        if avg_score >= 7:
            print("OVERALL ASSESSMENT: EXCELLENT - Ready for emergency deployment")
        elif avg_score >= 5:
            print("OVERALL ASSESSMENT: GOOD - Suitable for most emergency scenarios")
        elif avg_score >= 3:
            print("OVERALL ASSESSMENT: FAIR - Needs improvement for critical situations")
        else:
            print("OVERALL ASSESSMENT: POOR - Requires significant training enhancement")

def main():
    """Main function to run scenario testing"""
    tester = EmergencyScenarioTester()
    tester.run_all_scenarios()

if __name__ == "__main__":
    main()

