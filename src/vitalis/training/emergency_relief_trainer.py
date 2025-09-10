#!/usr/bin/env python3
"""
Emergency Relief AI Fine-tuning Pipeline
Comprehensive training system for GPT-OSS 20B emergency relief specialization
Optimized for M4 MacBook Pro with robust error handling and monitoring
"""

import os
import json
import logging
import time
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling,
    get_linear_schedule_with_warmup
)
from transformers.trainer_callback import TrainerCallback
import numpy as np
from typing import Dict, List, Optional, Any
import warnings
from pathlib import Path
import psutil
import gc

warnings.filterwarnings("ignore")

class EmergencyReliefDataset(Dataset):
    """
    Custom dataset for emergency relief training data
    Handles conversation format and proper tokenization
    """
    
    def __init__(self, data_path: str, tokenizer, max_length: int = 1024):
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Load training data
        with open(data_path, 'r') as f:
            raw_data = json.load(f)
        
        self.examples = raw_data.get('training_data', [])
        
        # System prompt for emergency relief context
        self.system_prompt = (
            "You are an expert emergency relief coordinator. Provide detailed, "
            "actionable guidance for disaster response, resource coordination, "
            "and emergency management. Always prioritize safety and follow "
            "established protocols."
        )
        
        # Preprocess all examples
        self.processed_examples = self._preprocess_examples()
        
        logging.info(f"Loaded {len(self.processed_examples)} training examples")
    
    def _preprocess_examples(self) -> List[Dict]:
        """Preprocess examples into chat format"""
        processed = []
        
        for example in self.examples:
            # Create conversation format
            conversation = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": example.get('instruction', '')},
                {"role": "assistant", "content": example.get('response', '')}
            ]
            
            # Apply chat template
            try:
                formatted_text = self.tokenizer.apply_chat_template(
                    conversation,
                    tokenize=False,
                    add_generation_prompt=False
                )
                processed.append({
                    'text': formatted_text,
                    'metadata': example.get('metadata', {})
                })
            except Exception as e:
                logging.warning(f"Failed to process example: {e}")
                continue
        
        return processed
    
    def __len__(self):
        return len(self.processed_examples)
    
    def __getitem__(self, idx):
        example = self.processed_examples[idx]
        
        # Tokenize
        encoding = self.tokenizer(
            example['text'],
            truncation=True,
            max_length=self.max_length,
            padding='max_length',
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': encoding['input_ids'].flatten().clone()
        }

class MemoryMonitorCallback(TrainerCallback):
    """
    Callback to monitor memory usage during training
    Critical for M4 MacBook Pro memory management
    """
    
    def __init__(self, log_interval: int = 1):
        self.log_interval = log_interval
        self.step_count = 0
    
    def on_step_begin(self, args, state, control, **kwargs):
        """Log before each step starts"""
        print(f"PROCESSING Starting step {state.global_step + 1}/21...")
    
    def on_step_end(self, args, state, control, **kwargs):
        self.step_count += 1
        
        if self.step_count % self.log_interval == 0:
            # Get memory usage
            memory_info = psutil.virtual_memory()
            memory_percent = memory_info.percent
            memory_used_gb = memory_info.used / (1024**3)
            memory_total_gb = memory_info.total / (1024**3)
            
            # Get MPS memory if available
            mps_memory = "N/A"
            if torch.backends.mps.is_available():
                try:
                    mps_memory = f"{torch.mps.current_allocated_memory() / (1024**3):.2f}GB"
                except:
                    pass
            
            print(f"METRICS Step {state.global_step}: Memory {memory_used_gb:.2f}/{memory_total_gb:.2f}GB ({memory_percent:.1f}%), MPS: {mps_memory}")
            logging.info(f"Step {state.global_step}: Memory {memory_used_gb:.2f}/{memory_total_gb:.2f}GB ({memory_percent:.1f}%), MPS: {mps_memory}")
            
            # Force garbage collection if memory usage is high
            if memory_percent > 80:
                logging.warning("High memory usage detected, forcing garbage collection")
                gc.collect()
                if torch.backends.mps.is_available():
                    torch.mps.empty_cache()

class EmergencyReliefTrainer:
    """
    Main trainer class for emergency relief AI fine-tuning
    Handles model loading, training, and validation with robust error handling
    """
    
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.setup_logging()
        
        # Initialize components
        self.tokenizer = None
        self.model = None
        self.dataset = None
        self.trainer = None
        
        logging.info("Emergency Relief Trainer initialized")
        logging.info(f"Configuration: {json.dumps(self.config, indent=2)}")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load training configuration"""
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = Path(self.config['output_dir']) / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"training_{int(time.time())}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def load_tokenizer(self) -> bool:
        """Load tokenizer with error handling"""
        try:
            logging.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config['model_path'],
                local_files_only=True,
                trust_remote_code=True
            )
            
            # Ensure pad token is set
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            logging.info("COMPLETED Tokenizer loaded successfully")
            return True
            
        except Exception as e:
            logging.error(f"FAILED Failed to load tokenizer: {e}")
            return False
    
    def load_model(self) -> bool:
        """Load model with multiple fallback strategies"""
        logging.info("Loading GPT-OSS 20B model...")
        
        # Try different loading strategies
        strategies = [
            {
                "name": "MPS GPU Optimized (Apple Silicon)",
                "device_map": {"": "mps"} if torch.backends.mps.is_available() else "cpu",
                "torch_dtype": torch.bfloat16,
                "low_cpu_mem_usage": True
            },
            {
                "name": "CPU BF16 Fallback",
                "device_map": "cpu",
                "torch_dtype": torch.bfloat16,
                "low_cpu_mem_usage": True
            },
            {
                "name": "CPU Float32 Safe Fallback",
                "device_map": "cpu", 
                "torch_dtype": torch.float32,
                "low_cpu_mem_usage": True
            }
        ]
        
        for strategy in strategies:
            try:
                logging.info(f"Trying: {strategy['name']}")
                
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.config['model_path'],
                    local_files_only=True,
                    trust_remote_code=True,
                    **{k: v for k, v in strategy.items() if k != 'name'}
                )
                
                # Ensure consistent dtypes across all model components
                target_dtype = strategy.get('torch_dtype', torch.bfloat16)
                
                # Convert model to target dtype carefully
                logging.info(f"Converting model to {target_dtype}")
                self.model = self.model.to(dtype=target_dtype)
                
                # Verify all parameters have the same dtype
                param_dtypes = {str(param.dtype) for param in self.model.parameters()}
                logging.info(f"Model parameter dtypes after conversion: {param_dtypes}")
                
                # Enable gradient checkpointing for memory efficiency
                if hasattr(self.model, 'gradient_checkpointing_enable'):
                    self.model.gradient_checkpointing_enable()
                
                logging.info(f"COMPLETED Model loaded successfully with {strategy['name']}")
                logging.info(f"Model device: {next(self.model.parameters()).device}")
                logging.info(f"Model dtype: {next(self.model.parameters()).dtype}")
                
                return True
                
            except Exception as e:
                logging.warning(f"FAILED {strategy['name']} failed: {str(e)[:100]}...")
                continue
        
        logging.error("FAILED All model loading strategies failed")
        return False
    
    def prepare_dataset(self) -> bool:
        """Prepare training dataset"""
        try:
            logging.info("Preparing training dataset...")
            
            self.dataset = EmergencyReliefDataset(
                data_path=self.config['data_path'],
                tokenizer=self.tokenizer,
                max_length=self.config['max_length']
            )
            
            # Split into train/validation
            dataset_size = len(self.dataset)
            train_size = int(0.9 * dataset_size)
            val_size = dataset_size - train_size
            
            self.train_dataset, self.val_dataset = torch.utils.data.random_split(
                self.dataset, [train_size, val_size]
            )
            
            logging.info(f"COMPLETED Dataset prepared: {train_size} train, {val_size} validation examples")
            return True
            
        except Exception as e:
            logging.error(f"FAILED Failed to prepare dataset: {e}")
            return False
    
    def setup_trainer(self) -> bool:
        """Setup the Hugging Face trainer"""
        try:
            logging.info("Setting up trainer...")
            
            # Training arguments optimized for M4 MacBook Pro
            training_args = TrainingArguments(
                output_dir=self.config['output_dir'],
                overwrite_output_dir=True,
                num_train_epochs=self.config['num_epochs'],
                per_device_train_batch_size=self.config['batch_size'],
                per_device_eval_batch_size=self.config['batch_size'],
                gradient_accumulation_steps=self.config['gradient_accumulation_steps'],
                learning_rate=self.config['learning_rate'],
                weight_decay=0.01,
                warmup_steps=self.config['warmup_steps'],
                logging_steps=self.config['logging_steps'],
                save_steps=self.config['save_steps'],
                eval_steps=self.config['eval_steps'],
                save_total_limit=3,
                eval_strategy="steps",
                load_best_model_at_end=True,
                metric_for_best_model="eval_loss",
                greater_is_better=False,
                fp16=False,  # Don't use fp16
                bf16=True,   # Use bfloat16 - Apple Silicon native format
                dataloader_pin_memory=False,  # Better for Apple Silicon
                remove_unused_columns=False,
                report_to=None,  # Disable wandb/tensorboard for now
                ddp_find_unused_parameters=False,
            )
            
            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer,
                mlm=False,
                pad_to_multiple_of=8
            )
            
            # Create trainer
            self.trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=self.train_dataset,
                eval_dataset=self.val_dataset,
                data_collator=data_collator,
                callbacks=[MemoryMonitorCallback(log_interval=1)]
            )
            
            logging.info("COMPLETED Trainer setup complete")
            return True
            
        except Exception as e:
            logging.error(f"FAILED Failed to setup trainer: {e}")
            return False
    
    def train(self) -> bool:
        """Execute the training process"""
        try:
            logging.info("LAUNCH Starting emergency relief AI training...")
            logging.info(f"Training on {len(self.train_dataset)} examples")
            logging.info(f"Validation on {len(self.val_dataset)} examples")
            
            # Start training
            train_result = self.trainer.train()
            
            logging.info("COMPLETED Training completed successfully!")
            logging.info(f"Final train loss: {train_result.training_loss:.4f}")
            
            # Save the final model
            self.save_model()
            
            return True
            
        except Exception as e:
            logging.error(f"FAILED Training failed: {e}")
            return False
    
    def save_model(self):
        """Save the fine-tuned model"""
        try:
            logging.info("Saving fine-tuned model...")
            
            # Save model and tokenizer
            output_path = Path(self.config['output_dir']) / 'emergency_relief_model'
            output_path.mkdir(parents=True, exist_ok=True)
            
            self.trainer.save_model(str(output_path))
            self.tokenizer.save_pretrained(str(output_path))
            
            # Save training config
            with open(output_path / 'training_config.json', 'w') as f:
                json.dump(self.config, f, indent=2)
            
            logging.info(f"COMPLETED Model saved to {output_path}")
            
        except Exception as e:
            logging.error(f"FAILED Failed to save model: {e}")
    
    def validate_model(self) -> bool:
        """Validate the trained model with emergency scenarios"""
        try:
            logging.info("Validating trained model...")
            
            test_prompts = [
                "How do you coordinate evacuation during a wildfire?",
                "What are the essential supplies for emergency shelter setup?",
                "How do you manage volunteers during disaster response?",
                "What are the steps for medical triage in mass casualties?",
                "How do you establish communication protocols during a disaster?"
            ]
            
            self.model.eval()
            
            for i, prompt in enumerate(test_prompts, 1):
                logging.info(f"Test {i}: {prompt}")
                
                # Format as conversation
                conversation = [
                    {"role": "system", "content": "You are an expert emergency relief coordinator."},
                    {"role": "user", "content": prompt}
                ]
                
                # Tokenize
                formatted_prompt = self.tokenizer.apply_chat_template(
                    conversation,
                    tokenize=False,
                    add_generation_prompt=True
                )
                
                inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
                
                # Generate response
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs.input_ids,
                        max_new_tokens=150,
                        temperature=0.7,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                response_only = response[len(formatted_prompt):].strip()
                
                logging.info(f"Response: {response_only[:200]}...")
                logging.info("-" * 50)
            
            logging.info("COMPLETED Model validation completed")
            return True
            
        except Exception as e:
            logging.error(f"FAILED Model validation failed: {e}")
            return False
    
    def run_complete_pipeline(self) -> bool:
        """Run the complete training pipeline"""
        logging.info("LAUNCH STARTING EMERGENCY RELIEF AI TRAINING PIPELINE")
        logging.info("=" * 60)
        
        pipeline_steps = [
            ("Loading Tokenizer", self.load_tokenizer),
            ("Loading Model", self.load_model),
            ("Preparing Dataset", self.prepare_dataset),
            ("Setting up Trainer", self.setup_trainer),
            ("Training Model", self.train),
            ("Validating Model", self.validate_model)
        ]
        
        for step_name, step_func in pipeline_steps:
            logging.info(f"PROCESSING {step_name}...")
            
            start_time = time.time()
            success = step_func()
            duration = time.time() - start_time
            
            if success:
                logging.info(f"COMPLETED {step_name} completed in {duration:.2f}s")
            else:
                logging.error(f"FAILED {step_name} failed after {duration:.2f}s")
                return False
            
            logging.info("-" * 40)
        
        logging.info("SUCCESS EMERGENCY RELIEF AI TRAINING COMPLETED SUCCESSFULLY!")
        logging.info("=" * 60)
        
        return True

def main():
    """Main entry point"""
    # Set up paths
    config_path = "./config/emergency_relief_training_config.json"
    
    # Create trainer and run pipeline
    trainer = EmergencyReliefTrainer(config_path)
    success = trainer.run_complete_pipeline()
    
    if success:
        print("\nSUCCESS Emergency Relief AI training completed successfully!")
        print(f"FOLDER Model saved to: {trainer.config['output_dir']}/emergency_relief_model")
        print("LAUNCH Ready for deployment!")
    else:
        print("\nFAILED Training failed. Check logs for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
