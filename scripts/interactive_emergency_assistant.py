#!/usr/bin/env python3
"""
Interactive Emergency Relief AI Assistant
User-friendly interface for testing the Emergency Relief AI as real users would
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from peft import PeftModel
import warnings
import time
import os
import sys
warnings.filterwarnings("ignore")

class EmergencyReliefAssistant:
    """Interactive Emergency Relief AI Assistant"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.loaded = False
        
    def load_model(self):
        """Load the Emergency Relief AI model"""
        base_model_path = "./models/gpt-oss-20b"
        lora_model_path = "./models/emergency_relief_fine_tuned/emergency_relief_lora"
        
        print("=" * 60)
        print("EMERGENCY RELIEF AI ASSISTANT")
        print("=" * 60)
        print("Loading Emergency Relief AI...")
        print("Please wait while we prepare your emergency assistance...")
        
        try:
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
            print("- Loading base emergency response model...")
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_path,
                local_files_only=True,
                trust_remote_code=True,
                device_map="cpu",
                torch_dtype=torch.bfloat16,
                low_cpu_mem_usage=True
            )
            
            # Load emergency relief specialization
            print("- Loading emergency relief specialization...")
            self.model = PeftModel.from_pretrained(
                base_model,
                lora_model_path,
                torch_dtype=torch.bfloat16
            )
            
            # Configure for optimal emergency response
            self.generation_config = GenerationConfig(
                max_new_tokens=150,
                min_new_tokens=20,
                temperature=0.3,  # More focused responses for emergencies
                do_sample=True,
                top_p=0.8,
                top_k=40,
                repetition_penalty=1.05,
                length_penalty=1.0,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=[200002, 199999],
                use_cache=True,
                early_stopping=True
            )
            
            print("Emergency Relief AI loaded successfully!")
            print("=" * 60)
            self.loaded = True
            return True
            
        except Exception as e:
            print(f"Failed to load Emergency Relief AI: {e}")
            print("Please check model files and try again.")
            return False
    
    def generate_response(self, user_input):
        """Generate emergency relief guidance"""
        if not self.loaded:
            return "Emergency Relief AI is not loaded. Please restart the assistant."
        
        try:
            # Create emergency coordinator prompt
            conversation = [
                {
                    "role": "system",
                    "content": "You are an expert Emergency Relief Coordinator. You provide clear, actionable guidance for disaster response, resource coordination, and emergency management. Always prioritize safety and follow established emergency protocols. Provide step-by-step instructions when appropriate."
                },
                {
                    "role": "user", 
                    "content": user_input
                }
            ]
            
            # Format using chat template
            prompt = self.tokenizer.apply_chat_template(
                conversation,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # Tokenize
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=1024
            )
            
            print("Generating emergency guidance...")
            start_time = time.time()
            
            # Generate with timeout protection
            with torch.no_grad():
                try:
                    # Use threading for timeout
                    import threading
                    import queue
                    
                    result_queue = queue.Queue()
                    
                    def generate_worker():
                        try:
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
                    thread.join(timeout=45)  # 45 second timeout for user experience
                    
                    if thread.is_alive():
                        return "I apologize, but generating emergency guidance is taking longer than expected. This may be due to system resources. Please try a shorter, more specific question."
                    
                    try:
                        result_type, result = result_queue.get_nowait()
                        if result_type == 'success':
                            # Decode response
                            generated_text = self.tokenizer.decode(result[0], skip_special_tokens=True)
                            response = generated_text[len(prompt):].strip()
                            
                            # Clean up response
                            for token in ["<|return|>", "<|endoftext|>", "<|call|>"]:
                                response = response.replace(token, "")
                            response = response.strip()
                            
                            generation_time = time.time() - start_time
                            
                            if response and len(response) > 10:
                                return f"{response}\n\n[Response generated in {generation_time:.1f}s]"
                            else:
                                return "I'm having difficulty generating a complete response. Please try rephrasing your emergency question or ask for specific guidance."
                        else:
                            return f"Emergency guidance system encountered an error: {result}"
                    except queue.Empty:
                        return "Emergency response generation failed to complete. Please try again with a more specific question."
                        
                except Exception as e:
                    return f"Emergency Relief AI encountered an error: {e}"
                    
        except Exception as e:
            return f"Failed to process your emergency request: {e}"
    
    def run_interactive_session(self):
        """Run interactive emergency relief session"""
        if not self.load_model():
            return
        
        # Show emergency scenarios menu
        self.show_emergency_scenarios()
        
        print("\nEMERGENCY RELIEF AI READY")
        print("Ask me about any emergency situation and I'll provide guidance.")
        print("Type 'help' for example scenarios, 'quit' to exit.\n")
        
        while True:
            try:
                # Get user input
                user_input = input("🚨 Emergency Question: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nEmergency Relief AI session ended.")
                    print("Stay safe and be prepared!")
                    break
                    
                if user_input.lower() == 'help':
                    self.show_emergency_scenarios()
                    continue
                
                if user_input.lower() == 'scenarios':
                    self.show_realistic_scenarios()
                    continue
                
                # Generate response
                print("\n" + "=" * 50)
                print("EMERGENCY GUIDANCE:")
                print("=" * 50)
                
                response = self.generate_response(user_input)
                print(response)
                print("=" * 50)
                print()
                
            except KeyboardInterrupt:
                print("\n\nEmergency Relief AI session interrupted.")
                print("Stay safe!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                print("Please try again.\n")
    
    def show_emergency_scenarios(self):
        """Show example emergency scenarios"""
        print("\n" + "=" * 60)
        print("EXAMPLE EMERGENCY SCENARIOS:")
        print("=" * 60)
        scenarios = [
            "How do I coordinate evacuation during a wildfire?",
            "What supplies do I need for emergency shelter setup?",
            "How do I manage volunteers during disaster response?",
            "What are the steps for medical triage in mass casualties?",
            "How do I establish communication during power outages?",
            "What's the protocol for water contamination emergencies?",
            "How do I organize emergency food distribution?",
            "What safety measures are needed for flood rescue?",
            "How do I set up an emergency command center?",
            "What's the evacuation procedure for high-rise buildings?"
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"{i:2d}. {scenario}")
        
        print("\nCommands:")
        print("- 'help' - Show this menu")
        print("- 'scenarios' - Show realistic emergency situations")
        print("- 'quit' - Exit the assistant")
        print("=" * 60)
    
    def show_realistic_scenarios(self):
        """Show realistic emergency situations for testing"""
        print("\n" + "=" * 60)
        print("REALISTIC EMERGENCY SITUATIONS:")
        print("=" * 60)
        situations = [
            {
                "title": "Wildfire Approaching Community",
                "prompt": "A wildfire is 2 miles from our town of 5,000 people. Winds are 25 mph. We have 4 hours before expected arrival. What do we do?"
            },
            {
                "title": "Flood Emergency Response", 
                "prompt": "Our town is flooding rapidly. Water is 3 feet deep in downtown. 200 people need evacuation. What's our action plan?"
            },
            {
                "title": "Earthquake Aftermath",
                "prompt": "6.2 earthquake just hit. Multiple building collapses. Power is out. Phone lines down. How do we coordinate rescue efforts?"
            },
            {
                "title": "Mass Casualty Incident",
                "prompt": "Bus accident with 40 injured people. Local hospital has 20-bed ER. What's the triage and treatment protocol?"
            },
            {
                "title": "Hurricane Preparation",
                "prompt": "Category 3 hurricane hitting in 18 hours. Coastal town of 12,000. What evacuation and shelter protocols should we follow?"
            }
        ]
        
        for i, situation in enumerate(situations, 1):
            print(f"{i}. {situation['title']}")
            print(f"   Scenario: {situation['prompt']}")
            print()
        
        print("Copy and paste any scenario above to test the AI's response.")
        print("=" * 60)

def main():
    """Main function to run the interactive assistant"""
    assistant = EmergencyReliefAssistant()
    assistant.run_interactive_session()

if __name__ == "__main__":
    main()

