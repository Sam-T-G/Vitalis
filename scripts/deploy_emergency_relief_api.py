#!/usr/bin/env python3
"""
Emergency Relief AI Deployment API
Simple Flask API for serving the fine-tuned emergency relief model
"""

import os
import json
import torch
import logging
from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM
import time
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)

class EmergencyReliefAPI:
    """
    API class for serving emergency relief AI model
    """
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        self.is_loaded = False
        
        # Load model on initialization
        self.load_model()
    
    def load_model(self):
        """Load the fine-tuned model"""
        try:
            logging.info(f"Loading model from {self.model_path}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                local_files_only=True,
                trust_remote_code=True
            )
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                local_files_only=True,
                trust_remote_code=True,
                torch_dtype=torch.bfloat16,
                device_map="auto",
                low_cpu_mem_usage=True
            )
            
            self.is_loaded = True
            logging.info("COMPLETED Model loaded successfully")
            
        except Exception as e:
            logging.error(f"FAILED Failed to load model: {e}")
            self.is_loaded = False
    
    def generate_response(self, prompt: str, max_tokens: int = 300) -> dict:
        """Generate emergency relief guidance"""
        if not self.is_loaded:
            return {
                "error": "Model not loaded",
                "response": None,
                "metadata": None
            }
        
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
            
            return {
                "error": None,
                "response": response_only,
                "metadata": {
                    "generation_time": generation_time,
                    "prompt_length": len(formatted_prompt),
                    "response_length": len(response_only),
                    "model_path": self.model_path
                }
            }
            
        except Exception as e:
            logging.error(f"FAILED Generation failed: {e}")
            return {
                "error": str(e),
                "response": None,
                "metadata": None
            }

# Initialize Flask app
app = Flask(__name__)

# Initialize API (will be set after model path is determined)
api = None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    if api and api.is_loaded:
        return jsonify({
            "status": "healthy",
            "model_loaded": True,
            "model_path": api.model_path
        })
    else:
        return jsonify({
            "status": "unhealthy",
            "model_loaded": False,
            "error": "Model not loaded"
        }), 500

@app.route('/emergency-guidance', methods=['POST'])
def get_emergency_guidance():
    """Main endpoint for emergency relief guidance"""
    try:
        # Check if model is loaded
        if not api or not api.is_loaded:
            return jsonify({
                "error": "Model not loaded",
                "response": None
            }), 500
        
        # Get request data
        data = request.json
        if not data or 'prompt' not in data:
            return jsonify({
                "error": "Missing 'prompt' in request body",
                "response": None
            }), 400
        
        prompt = data['prompt']
        max_tokens = data.get('max_tokens', 300)
        
        # Validate inputs
        if not prompt.strip():
            return jsonify({
                "error": "Empty prompt provided",
                "response": None
            }), 400
        
        if max_tokens < 10 or max_tokens > 1000:
            return jsonify({
                "error": "max_tokens must be between 10 and 1000",
                "response": None
            }), 400
        
        # Generate response
        result = api.generate_response(prompt, max_tokens)
        
        if result["error"]:
            return jsonify(result), 500
        else:
            return jsonify({
                "prompt": prompt,
                "response": result["response"],
                "metadata": result["metadata"]
            })
    
    except Exception as e:
        return jsonify({
            "error": f"Server error: {str(e)}",
            "response": None
        }), 500

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint with sample emergency scenario"""
    test_prompt = "What are the first steps to take when coordinating disaster response?"
    
    result = api.generate_response(test_prompt, 200)
    
    return jsonify({
        "test_prompt": test_prompt,
        "response": result["response"],
        "metadata": result["metadata"],
        "error": result["error"]
    })

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        "service": "Emergency Relief AI API",
        "version": "1.0.0",
        "model_loaded": api.is_loaded if api else False,
        "endpoints": {
            "/health": "GET - Health check",
            "/emergency-guidance": "POST - Get emergency relief guidance",
            "/test": "GET - Test with sample scenario"
        },
        "usage": {
            "example_request": {
                "method": "POST",
                "url": "/emergency-guidance",
                "body": {
                    "prompt": "How do you set up an emergency shelter?",
                    "max_tokens": 300
                }
            }
        }
    })

def main():
    """Main function to start the API server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Emergency Relief AI API Server")
    parser.add_argument(
        "--model-path",
        default="./models/emergency_relief_fine_tuned/emergency_relief_model",
        help="Path to the fine-tuned model"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to run the server on"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to run the server on"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run in debug mode"
    )
    
    args = parser.parse_args()
    
    # Check if model exists
    if not os.path.exists(args.model_path):
        print(f"FAILED Model not found at: {args.model_path}")
        print("IDEA Make sure to train the model first using train_emergency_relief_ai.py")
        return 1
    
    # Initialize API
    global api
    print(f"LAUNCH Starting Emergency Relief AI API...")
    print(f"FOLDER Model path: {args.model_path}")
    
    api = EmergencyReliefAPI(args.model_path)
    
    if not api.is_loaded:
        print("FAILED Failed to load model. Check logs for details.")
        return 1
    
    print("COMPLETED Model loaded successfully!")
    print(f" Starting server on http://{args.host}:{args.port}")
    print("CHECKLIST Available endpoints:")
    print(f"   - GET  http://{args.host}:{args.port}/health")
    print(f"   - POST http://{args.host}:{args.port}/emergency-guidance")
    print(f"   - GET  http://{args.host}:{args.port}/test")
    
    # Start Flask server
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
        threaded=True
    )
    
    return 0

if __name__ == "__main__":
    exit(main())
