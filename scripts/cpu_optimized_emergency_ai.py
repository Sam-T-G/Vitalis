#!/usr/bin/env python3
"""
CPU-Optimized Emergency Relief AI
Workaround for MoE architecture limitations on CPU
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import warnings
import time
import gc
import threading
import queue
warnings.filterwarnings("ignore")

class CPUOptimizedEmergencyAI:
    """CPU-optimized Emergency Relief AI with MoE workarounds"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.loaded = False
        
        # Pre-generated emergency responses for critical situations
        self.emergency_templates = {
            "wildfire": """WILDFIRE EVACUATION PROTOCOL:
1. IMMEDIATE (0-30 min): Sound evacuation alarms, activate emergency broadcast
2. EVACUATION ROUTES: Open all designated routes, deploy traffic control
3. VULNERABLE POPULATIONS: Priority evacuation for elderly, disabled, hospitals
4. TRANSPORTATION: Deploy all available buses, coordinate with transport services
5. SHELTER: Activate pre-designated evacuation centers, ensure capacity
6. COMMUNICATION: Maintain regular updates via radio, mobile alerts
7. SAFETY: Ensure all evacuation routes remain clear of fire danger""",
            
            "flood": """FLOOD EMERGENCY RESPONSE:
1. IMMEDIATE RESCUE: Deploy boats/high vehicles to stranded locations
2. EVACUATION: Move people to higher ground, use vertical evacuation if needed
3. COMMUNICATION: Establish emergency communication center
4. MEDICAL: Set up triage areas, ensure medical access routes
5. UTILITIES: Shut off electricity to flooded areas, monitor water safety
6. COORDINATION: Deploy search and rescue teams systematically
7. SHELTER: Open emergency shelters with capacity for displaced persons""",
            
            "earthquake": """EARTHQUAKE RESPONSE PROTOCOL:
1. IMMEDIATE SAFETY: Check for injuries, aftershock precautions
2. SEARCH AND RESCUE: Deploy teams to collapsed buildings systematically
3. COMMUNICATION: Establish backup communication systems
4. MEDICAL TRIAGE: Set up field hospitals, categorize injuries by severity
5. UTILITIES: Assess and shut off damaged gas lines, electrical hazards
6. COORDINATION: Establish incident command center
7. RESOURCES: Request mutual aid, coordinate with regional emergency services""",
            
            "mass_casualty": """MASS CASUALTY INCIDENT PROTOCOL:
1. SCENE SAFETY: Secure area, ensure no ongoing hazards
2. TRIAGE: Implement START triage (Simple Triage and Rapid Treatment)
   - RED: Immediate life-threatening, can be saved
   - YELLOW: Delayed treatment, stable
   - GREEN: Walking wounded, minor injuries
   - BLACK: Deceased or unsalvageable
3. TRANSPORT: Prioritize RED patients to trauma centers
4. COMMUNICATION: Notify hospitals, request additional resources
5. COMMAND: Establish unified command structure""",
            
            "chemical": """HAZMAT EMERGENCY RESPONSE:
1. EVACUATION PERIMETER: Establish zones based on wind direction and chemical type
2. DECONTAMINATION: Set up decon stations for exposed persons
3. PPE: Ensure all responders use appropriate protective equipment
4. AIR MONITORING: Continuously monitor air quality
5. MEDICAL: Treat exposed individuals, establish treatment protocols
6. CONTAINMENT: Prevent further spread of contamination
7. COMMUNICATION: Notify specialized hazmat teams""",
            
            "general": """GENERAL EMERGENCY RESPONSE:
1. ASSESS SITUATION: Determine scope, severity, and immediate threats
2. ENSURE SAFETY: Protect responders and public from additional harm
3. ACTIVATE RESOURCES: Contact appropriate emergency services
4. ESTABLISH COMMAND: Set up incident command structure
5. COMMUNICATE: Notify authorities and public as appropriate
6. DOCUMENT: Record actions taken for after-action review
7. MONITOR: Continuously assess changing conditions"""
        }
    
    def load_model_lightweight(self):
        """Load model with CPU optimizations"""
        print("Loading Emergency Relief AI (CPU-Optimized Mode)...")
        print("Note: Using hybrid approach due to MoE architecture limitations")
        
        try:
            base_model_path = "./models/gpt-oss-20b"
            lora_model_path = "./models/emergency_relief_fine_tuned/emergency_relief_lora"
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                base_model_path,
                local_files_only=True,
                trust_remote_code=True
            )
            
            # Configure tokenizer
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = "<|endoftext|>"
                self.tokenizer.pad_token_id = 199999
            self.tokenizer.padding_side = "left"
            
            # Try to load model with extreme CPU optimizations
            print("Loading model with CPU optimizations...")
            
            # Load with minimal memory footprint
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_path,
                local_files_only=True,
                trust_remote_code=True,
                device_map="cpu",
                torch_dtype=torch.float16,  # Use float16 to save memory
                low_cpu_mem_usage=True
            )
            
            # Load LoRA with matching precision
            self.model = PeftModel.from_pretrained(
                base_model,
                lora_model_path,
                torch_dtype=torch.float16
            )
            
            # Optimize for CPU inference
            self.model.eval()
            
            # Clear memory
            gc.collect()
            
            print("Model loaded successfully!")
            self.loaded = True
            return True
            
        except Exception as e:
            print(f"Model loading failed: {e}")
            print("Falling back to template-based responses...")
            return False
    
    def detect_emergency_type(self, text):
        """Detect emergency type from user input"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['fire', 'wildfire', 'blaze', 'burn']):
            return "wildfire"
        elif any(word in text_lower for word in ['flood', 'water', 'rain', 'dam', 'river']):
            return "flood"
        elif any(word in text_lower for word in ['earthquake', 'quake', 'shake', 'collapse']):
            return "earthquake"
        elif any(word in text_lower for word in ['accident', 'crash', 'casualty', 'injured', 'victims']):
            return "mass_casualty"
        elif any(word in text_lower for word in ['chemical', 'spill', 'hazmat', 'toxic', 'gas']):
            return "chemical"
        else:
            return "general"
    
    def generate_emergency_response_hybrid(self, user_input):
        """Generate response using hybrid AI + template approach"""
        
        # Try AI generation first (with very short timeout)
        if self.loaded:
            ai_response = self.try_ai_generation(user_input, timeout=10)
            if ai_response:
                return ai_response
        
        # Fallback to intelligent template matching
        emergency_type = self.detect_emergency_type(user_input)
        template_response = self.emergency_templates[emergency_type]
        
        # Customize template based on input
        customized_response = self.customize_template_response(user_input, template_response)
        
        return customized_response
    
    def try_ai_generation(self, user_input, timeout=10):
        """Try AI generation with very short timeout"""
        try:
            # Ultra-minimal prompt to reduce computation
            simple_prompt = f"Emergency: {user_input}\nResponse:"
            
            inputs = self.tokenizer(simple_prompt, return_tensors="pt", max_length=100)
            
            result_queue = queue.Queue()
            
            def generate_worker():
                try:
                    with torch.no_grad():
                        # Extremely conservative generation parameters
                        outputs = self.model.generate(
                            inputs.input_ids,
                            max_new_tokens=20,  # Very small
                            min_new_tokens=5,
                            do_sample=False,  # Greedy for speed
                            use_cache=True,
                            pad_token_id=self.tokenizer.pad_token_id,
                            eos_token_id=200002
                        )
                    result_queue.put(('success', outputs))
                except Exception as e:
                    result_queue.put(('error', str(e)))
            
            thread = threading.Thread(target=generate_worker)
            thread.daemon = True
            thread.start()
            thread.join(timeout=timeout)
            
            if not thread.is_alive():
                try:
                    result_type, result = result_queue.get_nowait()
                    if result_type == 'success':
                        generated_text = self.tokenizer.decode(result[0], skip_special_tokens=True)
                        response = generated_text[len(simple_prompt):].strip()
                        if len(response) > 10:  # Valid response
                            return response
                except queue.Empty:
                    pass
            
            return None
            
        except Exception as e:
            return None
    
    def customize_template_response(self, user_input, template_response):
        """Customize template response based on user input details"""
        
        # Extract specific details from user input
        details = self.extract_emergency_details(user_input)
        
        # Add specific guidance based on details
        customized = template_response
        
        if details['timeframe']:
            customized = f"TIMEFRAME: {details['timeframe']}\n\n" + customized
        
        if details['population']:
            customized = f"AFFECTED POPULATION: {details['population']}\n\n" + customized
        
        if details['location']:
            customized = f"LOCATION: {details['location']}\n\n" + customized
        
        # Add specific guidance footer
        customized += f"\n\nADDITIONAL GUIDANCE:\n"
        customized += f"- Continuously reassess situation as it develops\n"
        customized += f"- Maintain clear communication with all responders\n"
        customized += f"- Document all actions for after-action review\n"
        customized += f"- Request additional resources early if needed"
        
        return customized
    
    def extract_emergency_details(self, text):
        """Extract specific details from emergency description"""
        import re
        
        details = {
            'timeframe': None,
            'population': None,
            'location': None
        }
        
        # Extract timeframes
        time_patterns = [
            r'(\d+)\s*(hour|hr|minute|min)',
            r'(immediately|urgent|now)',
            r'(\d+)\s*(days?|hours?|minutes?)'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                details['timeframe'] = match.group(0)
                break
        
        # Extract population numbers
        pop_patterns = [
            r'(\d+)\s*(people|person|resident|individual)',
            r'(school|hospital|building)',
            r'(\d+)\s*(student|patient|worker)'
        ]
        
        for pattern in pop_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                details['population'] = match.group(0)
                break
        
        # Extract location info
        loc_patterns = [
            r'(town|city|community|neighborhood|school|hospital)',
            r'(\d+)\s*(mile|km|block)',
            r'(downtown|residential|coastal)'
        ]
        
        for pattern in loc_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                details['location'] = match.group(0)
                break
        
        return details
    
    def run_interactive_session(self):
        """Run interactive emergency assistance session"""
        print("=" * 60)
        print("EMERGENCY RELIEF AI - CPU OPTIMIZED")
        print("=" * 60)
        print("Hybrid AI + Expert Template System")
        print("Optimized for CPU performance and reliable emergency guidance")
        print()
        
        # Load model (may fail, that's OK)
        self.load_model_lightweight()
        
        print("\nEMERGENCY RELIEF AI READY")
        print("Ask about any emergency situation for immediate guidance.")
        print("Type 'help' for examples, 'quit' to exit.\n")
        
        while True:
            try:
                user_input = input("Emergency Question: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nEmergency Relief AI session ended.")
                    print("Stay safe and be prepared!")
                    break
                    
                if user_input.lower() == 'help':
                    self.show_examples()
                    continue
                
                # Generate response
                print("\n" + "=" * 50)
                print("EMERGENCY GUIDANCE:")
                print("=" * 50)
                
                start_time = time.time()
                response = self.generate_emergency_response_hybrid(user_input)
                response_time = time.time() - start_time
                
                print(response)
                print("=" * 50)
                print(f"Response generated in {response_time:.1f}s")
                if self.loaded:
                    print("Source: Hybrid AI + Expert Templates")
                else:
                    print("Source: Expert Emergency Templates")
                print()
                
            except KeyboardInterrupt:
                print("\n\nEmergency Relief AI session interrupted.")
                print("Stay safe!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                print("Please try again.\n")
    
    def show_examples(self):
        """Show example emergency scenarios"""
        print("\n" + "=" * 60)
        print("EXAMPLE EMERGENCY SCENARIOS:")
        print("=" * 60)
        examples = [
            "Wildfire approaching town in 2 hours, 500 residents need evacuation",
            "Flash flood has trapped 50 people in school building",
            "Earthquake damaged buildings, multiple people trapped",
            "Chemical spill on highway near elementary school",
            "Mass casualty accident with 25 injured people",
            "Hurricane approaching coastal town in 24 hours"
        ]
        
        for i, example in enumerate(examples, 1):
            print(f"{i:2d}. {example}")
        
        print("\nType any emergency scenario for immediate guidance.")
        print("=" * 60)

def main():
    """Run the CPU-optimized emergency AI"""
    ai = CPUOptimizedEmergencyAI()
    ai.run_interactive_session()

if __name__ == "__main__":
    main()
