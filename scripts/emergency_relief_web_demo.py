#!/usr/bin/env python3
"""
Emergency Relief AI Web Demo
Simple web interface for user testing of the Emergency Relief AI
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from peft import PeftModel
import warnings
import time
import os
import threading
import queue
warnings.filterwarnings("ignore")

app = Flask(__name__)

class EmergencyReliefWebDemo:
    """Web demo for Emergency Relief AI"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.loaded = False
        self.loading = False
        
    def load_model(self):
        """Load the Emergency Relief AI model"""
        if self.loading or self.loaded:
            return self.loaded
            
        self.loading = True
        
        try:
            base_model_path = "./models/gpt-oss-20b"
            lora_model_path = "./models/emergency_relief_fine_tuned/emergency_relief_lora"
            
            print("Loading Emergency Relief AI model...")
            
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
                max_new_tokens=150,
                min_new_tokens=20,
                temperature=0.3,
                do_sample=True,
                top_p=0.8,
                repetition_penalty=1.05,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=[200002, 199999],
                early_stopping=True,
                use_cache=True
            )
            
            print("Emergency Relief AI loaded successfully!")
            self.loaded = True
            
        except Exception as e:
            print(f"Failed to load model: {e}")
            self.loaded = False
        finally:
            self.loading = False
            
        return self.loaded
    
    def generate_response(self, user_input):
        """Generate emergency relief guidance"""
        if not self.loaded:
            return {
                "success": False,
                "response": "Emergency Relief AI is still loading. Please wait a moment and try again.",
                "time": 0
            }
        
        try:
            conversation = [
                {
                    "role": "system",
                    "content": "You are an expert Emergency Relief Coordinator. Provide clear, actionable guidance for emergency situations. Focus on immediate safety steps and practical emergency response measures."
                },
                {
                    "role": "user", 
                    "content": user_input
                }
            ]
            
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
            thread.join(timeout=30)  # 30 second timeout for web interface
            
            generation_time = time.time() - start_time
            
            if thread.is_alive():
                return {
                    "success": False,
                    "response": "Response generation is taking longer than expected. Please try a shorter, more specific emergency question.",
                    "time": generation_time
                }
            
            try:
                result_type, result = result_queue.get_nowait()
                if result_type == 'success':
                    generated_text = self.tokenizer.decode(result[0], skip_special_tokens=True)
                    response = generated_text[len(prompt):].strip()
                    
                    # Clean response
                    for token in ["<|return|>", "<|endoftext|>", "<|call|>"]:
                        response = response.replace(token, "")
                    response = response.strip()
                    
                    if response and len(response) > 10:
                        return {
                            "success": True,
                            "response": response,
                            "time": generation_time
                        }
                    else:
                        return {
                            "success": False,
                            "response": "I'm having difficulty generating a complete response. Please try rephrasing your emergency question.",
                            "time": generation_time
                        }
                else:
                    return {
                        "success": False,
                        "response": f"Emergency guidance system error: {result}",
                        "time": generation_time
                    }
            except queue.Empty:
                return {
                    "success": False,
                    "response": "Emergency response generation failed to complete. Please try again.",
                    "time": generation_time
                }
                
        except Exception as e:
            return {
                "success": False,
                "response": f"Failed to process emergency request: {e}",
                "time": 0
            }

# Global demo instance
demo = EmergencyReliefWebDemo()

@app.route('/')
def index():
    """Main page"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Emergency Relief AI Demo</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5; 
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background: white; 
            padding: 30px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
        }
        h1 { 
            color: #d32f2f; 
            text-align: center; 
            margin-bottom: 10px; 
        }
        .subtitle { 
            text-align: center; 
            color: #666; 
            margin-bottom: 30px; 
        }
        .input-section { 
            margin-bottom: 20px; 
        }
        label { 
            display: block; 
            margin-bottom: 5px; 
            font-weight: bold; 
            color: #333; 
        }
        textarea { 
            width: 100%; 
            padding: 10px; 
            border: 2px solid #ddd; 
            border-radius: 5px; 
            font-size: 16px; 
            min-height: 100px; 
            box-sizing: border-box;
        }
        button { 
            background-color: #d32f2f; 
            color: white; 
            padding: 12px 24px; 
            border: none; 
            border-radius: 5px; 
            font-size: 16px; 
            cursor: pointer; 
            width: 100%;
        }
        button:hover { 
            background-color: #b71c1c; 
        }
        button:disabled { 
            background-color: #ccc; 
            cursor: not-allowed; 
        }
        .response-section { 
            margin-top: 30px; 
            padding: 20px; 
            background-color: #f8f9fa; 
            border-radius: 5px; 
            border-left: 4px solid #d32f2f; 
            display: none; 
        }
        .response-header { 
            font-weight: bold; 
            color: #d32f2f; 
            margin-bottom: 10px; 
        }
        .response-text { 
            line-height: 1.6; 
            white-space: pre-wrap; 
        }
        .response-meta { 
            margin-top: 15px; 
            font-size: 14px; 
            color: #666; 
        }
        .examples { 
            background-color: #e8f5e8; 
            padding: 20px; 
            border-radius: 5px; 
            margin-bottom: 20px; 
        }
        .examples h3 { 
            margin-top: 0; 
            color: #2e7d32; 
        }
        .example-item { 
            margin: 10px 0; 
            padding: 10px; 
            background: white; 
            border-radius: 3px; 
            cursor: pointer; 
            border: 1px solid #ddd; 
        }
        .example-item:hover { 
            background-color: #f0f8f0; 
        }
        .loading { 
            text-align: center; 
            color: #666; 
        }
        .error { 
            color: #d32f2f; 
        }
        .success { 
            color: #2e7d32; 
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Emergency Relief AI</h1>
        <p class="subtitle">Test the AI assistant for emergency response guidance</p>
        
        <div class="examples">
            <h3>Example Emergency Scenarios (Click to use):</h3>
            <div class="example-item" onclick="setExample('A wildfire is approaching our neighborhood. We have 2 hours to evacuate. What should we do first?')">
                Wildfire evacuation with 2 hours notice
            </div>
            <div class="example-item" onclick="setExample('Our town is flooding rapidly. 50 people are trapped in a school building. How do we coordinate rescue?')">
                Flood rescue coordination
            </div>
            <div class="example-item" onclick="setExample('Major earthquake just hit. Multiple buildings collapsed. Communication is down. What are our priorities?')">
                Earthquake emergency response
            </div>
            <div class="example-item" onclick="setExample('Bus accident with 25 injured people. Local hospital is overwhelmed. What is the triage protocol?')">
                Mass casualty triage
            </div>
            <div class="example-item" onclick="setExample('Chemical spill on highway near school. Unknown substance leaking. 200 people need evacuation. What steps do we take?')">
                Hazmat emergency response
            </div>
        </div>
        
        <div class="input-section">
            <label for="emergency-input">Describe your emergency situation:</label>
            <textarea id="emergency-input" placeholder="Example: A wildfire is approaching our town. We have 500 residents and 3 hours before expected arrival. What evacuation steps should we take?"></textarea>
        </div>
        
        <button onclick="getEmergencyGuidance()" id="submit-btn">Get Emergency Guidance</button>
        
        <div id="response-section" class="response-section">
            <div class="response-header">Emergency Response Guidance:</div>
            <div id="response-text" class="response-text"></div>
            <div id="response-meta" class="response-meta"></div>
        </div>
    </div>

    <script>
        function setExample(text) {
            document.getElementById('emergency-input').value = text;
        }
        
        async function getEmergencyGuidance() {
            const input = document.getElementById('emergency-input').value.trim();
            const submitBtn = document.getElementById('submit-btn');
            const responseSection = document.getElementById('response-section');
            const responseText = document.getElementById('response-text');
            const responseMeta = document.getElementById('response-meta');
            
            if (!input) {
                alert('Please describe your emergency situation');
                return;
            }
            
            // Show loading state
            submitBtn.disabled = true;
            submitBtn.textContent = 'Generating Emergency Guidance...';
            responseSection.style.display = 'block';
            responseText.innerHTML = '<div class="loading">Analyzing emergency situation and generating response...</div>';
            responseMeta.innerHTML = '';
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ input: input })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    responseText.innerHTML = '<div class="success">' + data.response + '</div>';
                    responseMeta.innerHTML = `Response generated in ${data.time.toFixed(1)} seconds`;
                } else {
                    responseText.innerHTML = '<div class="error">' + data.response + '</div>';
                    responseMeta.innerHTML = data.time > 0 ? `Failed after ${data.time.toFixed(1)} seconds` : '';
                }
                
            } catch (error) {
                responseText.innerHTML = '<div class="error">Error connecting to Emergency Relief AI: ' + error.message + '</div>';
                responseMeta.innerHTML = '';
            }
            
            // Reset button
            submitBtn.disabled = false;
            submitBtn.textContent = 'Get Emergency Guidance';
        }
        
        // Allow Enter key to submit (Ctrl+Enter for line breaks)
        document.getElementById('emergency-input').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.ctrlKey) {
                e.preventDefault();
                getEmergencyGuidance();
            }
        });
    </script>
</body>
</html>
    """

@app.route('/generate', methods=['POST'])
def generate():
    """Generate emergency response"""
    try:
        data = request.get_json()
        user_input = data.get('input', '')
        
        if not user_input:
            return jsonify({
                "success": False,
                "response": "No emergency situation provided",
                "time": 0
            })
        
        # Load model if not loaded
        if not demo.loaded and not demo.loading:
            demo.load_model()
        
        # Generate response
        result = demo.generate_response(user_input)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "response": f"Server error: {str(e)}",
            "time": 0
        })

@app.route('/status')
def status():
    """Check model status"""
    return jsonify({
        "loaded": demo.loaded,
        "loading": demo.loading
    })

def main():
    """Run the web demo"""
    print("Starting Emergency Relief AI Web Demo...")
    print("Loading model in background...")
    
    # Start loading model in background
    threading.Thread(target=demo.load_model, daemon=True).start()
    
    print("\nWeb demo will be available at: http://localhost:5000")
    print("Note: Model loading may take a few minutes")
    print("Press Ctrl+C to stop the demo")
    
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main()
