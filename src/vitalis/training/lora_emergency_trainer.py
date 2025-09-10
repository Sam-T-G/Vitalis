#!/usr/bin/env python3
"""
LoRA Emergency Relief AI Trainer
Memory-efficient fine-tuning using Parameter-Efficient Fine-Tuning (PEFT/LoRA)
Designed to work with large models on limited memory systems
"""

import os
import json
import logging
import time
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType, PeftModel
from torch.utils.data import Dataset
import numpy as np
from typing import Dict, List
import warnings
from pathlib import Path
import psutil
import gc

warnings.filterwarnings("ignore")

class EmergencyReliefDataset(Dataset):
    """Lightweight dataset for LoRA training"""
    
    def __init__(self, data_path: str, tokenizer, max_length: int = 512):
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        with open(data_path, 'r') as f:
            raw_data = json.load(f)
        
        self.examples = raw_data.get('training_data', [])
        
        self.system_prompt = (
            "You are an expert emergency relief coordinator. Provide detailed, "
            "actionable guidance for disaster response, resource coordination, "
            "and emergency management. Always prioritize safety and follow "
            "established protocols."
        )
        
        self.processed_examples = self._preprocess_examples()
        logging.info(f"Loaded {len(self.processed_examples)} training examples for LoRA")
    
    def _preprocess_examples(self) -> List[Dict]:
        processed = []
        
        for example in self.examples:
            conversation = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": example.get('instruction', '')},
                {"role": "assistant", "content": example.get('response', '')}
            ]
            
            try:
                formatted_text = self.tokenizer.apply_chat_template(
                    conversation,
                    tokenize=False,
                    add_generation_prompt=False
                )
                processed.append({'text': formatted_text})
            except Exception as e:
                logging.warning(f"Failed to process example: {e}")
                continue
        
        return processed
    
    def __len__(self):
        return len(self.processed_examples)
    
    def __getitem__(self, idx):
        example = self.processed_examples[idx]
        
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

class LoRAEmergencyTrainer:
    """
    Memory-efficient LoRA trainer for emergency relief AI
    """
    
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.setup_logging()
        
        self.tokenizer = None
        self.model = None
        self.peft_model = None
        self.dataset = None
        self.trainer = None
        
        logging.info("LoRA Emergency Relief Trainer initialized")
    
    def _load_config(self, config_path: str) -> Dict:
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def setup_logging(self):
        log_dir = Path(self.config['output_dir']) / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"lora_training_{int(time.time())}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def load_model_and_tokenizer(self) -> bool:
        """Load model and tokenizer with memory optimization"""
        try:
            logging.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config['model_path'],
                local_files_only=True,
                trust_remote_code=True
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            logging.info("COMPLETED Tokenizer loaded")
            
            logging.info("Loading base model for LoRA...")
            print("Loading model (this may take a few minutes)...")
            
            # Try MPS first, fallback to CPU
            try:
                if torch.backends.mps.is_available():
                    print("Attempting MPS (Apple Silicon GPU) loading...")
                    device_map = {"": "mps"}
                else:
                    print("PROCESSING Using CPU loading...")
                    device_map = "cpu"
                
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.config['model_path'],
                    local_files_only=True,
                    trust_remote_code=True,
                    device_map=device_map,
                    torch_dtype=torch.bfloat16,
                    low_cpu_mem_usage=True
                )
            except Exception as e:
                print(f"WARNING MPS loading failed: {e}")
                print("PROCESSING Falling back to CPU...")
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.config['model_path'],
                    local_files_only=True,
                    trust_remote_code=True,
                    device_map="cpu",
                    torch_dtype=torch.bfloat16,
                    low_cpu_mem_usage=True
                )
            
            # Ensure all model components use bfloat16
            self.model = self.model.to(dtype=torch.bfloat16)
            
            # Verify dtype consistency
            param_dtypes = {str(param.dtype) for param in self.model.parameters()}
            print(f"COMPLETED Model parameter dtypes: {param_dtypes}")
            
            logging.info("COMPLETED Base model loaded")
            print("COMPLETED Base model loaded successfully")
            
            return True
            
        except Exception as e:
            logging.error(f"FAILED Failed to load model: {e}")
            print(f"FAILED Failed to load model: {e}")
            return False
    
    def setup_lora(self) -> bool:
        """Set up LoRA configuration"""
        try:
            logging.info("Setting up LoRA configuration...")
            print("CONFIG Setting up LoRA for parameter-efficient training...")
            
            # LoRA configuration optimized for emergency relief training
            lora_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                inference_mode=False,
                r=8,  # Reduced rank for lower memory usage
                lora_alpha=16,  # Reduced scaling parameter
                lora_dropout=0.1,  # Dropout for regularization
                target_modules=["q_proj", "v_proj"],  # Fewer target modules for memory efficiency
                bias="none"
            )
            
            # Enable gradient checkpointing before applying LoRA
            if hasattr(self.model, 'gradient_checkpointing_enable'):
                self.model.gradient_checkpointing_enable()
                print("COMPLETED Gradient checkpointing enabled for memory efficiency")
            
            # Apply LoRA to the model
            self.peft_model = get_peft_model(self.model, lora_config)
            
            # Print trainable parameters
            trainable_params = self.peft_model.print_trainable_parameters()
            logging.info(f"LoRA setup complete: {trainable_params}")
            print("COMPLETED LoRA setup complete - only training a small subset of parameters!")
            
            return True
            
        except Exception as e:
            logging.error(f"FAILED LoRA setup failed: {e}")
            print(f"FAILED LoRA setup failed: {e}")
            return False
    
    def prepare_dataset(self) -> bool:
        """Prepare training dataset"""
        try:
            logging.info("Preparing training dataset...")
            print("LIBRARY Preparing emergency relief training data...")
            
            self.dataset = EmergencyReliefDataset(
                data_path=self.config['data_path'],
                tokenizer=self.tokenizer,
                max_length=512  # Reduced for memory efficiency
            )
            
            # Split dataset
            dataset_size = len(self.dataset)
            train_size = int(0.9 * dataset_size)
            val_size = dataset_size - train_size
            
            self.train_dataset, self.val_dataset = torch.utils.data.random_split(
                self.dataset, [train_size, val_size]
            )
            
            logging.info(f"COMPLETED Dataset prepared: {train_size} train, {val_size} validation")
            print(f"COMPLETED Dataset ready: {train_size} training, {val_size} validation examples")
            
            return True
            
        except Exception as e:
            logging.error(f"FAILED Dataset preparation failed: {e}")
            print(f"FAILED Dataset preparation failed: {e}")
            return False
    
    def setup_trainer(self) -> bool:
        """Setup the trainer with LoRA optimizations"""
        try:
            logging.info("Setting up LoRA trainer...")
            print("SETTINGS Setting up memory-efficient trainer...")
            
            # Training arguments optimized for LoRA and memory efficiency
            training_args = TrainingArguments(
                output_dir=self.config['output_dir'],
                overwrite_output_dir=True,
                num_train_epochs=3,
                per_device_train_batch_size=1,
                per_device_eval_batch_size=1,
                gradient_accumulation_steps=8,  # Larger accumulation for LoRA
                learning_rate=1e-4,  # Higher learning rate for LoRA
                weight_decay=0.01,
                warmup_steps=20,
                logging_steps=1,
                save_steps=10,
                eval_steps=10,
                save_total_limit=2,
                eval_strategy="steps",
                load_best_model_at_end=True,
                metric_for_best_model="eval_loss",
                greater_is_better=False,
                fp16=False,
                bf16=True,   # Use bfloat16 consistently with model
                dataloader_pin_memory=False,
                remove_unused_columns=False,
                report_to=None,
                ddp_find_unused_parameters=False,
                dataloader_num_workers=0,  # Reduce memory usage
            )
            
            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer,
                mlm=False,
                pad_to_multiple_of=8
            )
            
            # Create trainer
            self.trainer = Trainer(
                model=self.peft_model,
                args=training_args,
                train_dataset=self.train_dataset,
                eval_dataset=self.val_dataset,
                data_collator=data_collator
            )
            
            logging.info("COMPLETED LoRA trainer setup complete")
            print("COMPLETED Trainer ready for memory-efficient fine-tuning!")
            return True
            
        except Exception as e:
            logging.error(f"FAILED Trainer setup failed: {e}")
            print(f"FAILED Trainer setup failed: {e}")
            return False
    
    def train(self) -> bool:
        """Execute LoRA training"""
        try:
            logging.info("LAUNCH Starting LoRA emergency relief training...")
            print("LAUNCH Starting memory-efficient emergency relief training...")
            print(f"METRICS Training on {len(self.train_dataset)} examples")
            
            # Force garbage collection before training
            gc.collect()
            
            # Start training
            train_result = self.trainer.train()
            
            logging.info("COMPLETED LoRA training completed!")
            print("COMPLETED Emergency relief training completed successfully!")
            logging.info(f"Final train loss: {train_result.training_loss:.4f}")
            
            # Save the LoRA adapter
            self.save_lora_model()
            
            return True
            
        except Exception as e:
            logging.error(f"FAILED Training failed: {e}")
            print(f"FAILED Training failed: {e}")
            return False
    
    def save_lora_model(self):
        """Save the LoRA adapter"""
        try:
            logging.info("Saving LoRA adapter...")
            print("SAVE Saving emergency relief LoRA model...")
            
            output_path = Path(self.config['output_dir']) / 'emergency_relief_lora'
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Save LoRA adapter
            self.peft_model.save_pretrained(str(output_path))
            self.tokenizer.save_pretrained(str(output_path))
            
            # Save config
            with open(output_path / 'training_config.json', 'w') as f:
                json.dump(self.config, f, indent=2)
            
            logging.info(f"COMPLETED LoRA model saved to {output_path}")
            print(f"COMPLETED Model saved to {output_path}")
            
        except Exception as e:
            logging.error(f"FAILED Failed to save model: {e}")
            print(f"FAILED Failed to save model: {e}")
    
    def test_model(self) -> bool:
        """Test the trained model"""
        try:
            logging.info("Testing trained LoRA model...")
            print("TEST Testing emergency relief AI...")
            
            test_prompts = [
                "How do you coordinate evacuation during a wildfire?",
                "What are essential supplies for emergency shelter setup?"
            ]
            
            self.peft_model.eval()
            
            for prompt in test_prompts:
                print(f"\nSEARCH Testing: {prompt}")
                
                conversation = [
                    {"role": "system", "content": "You are an expert emergency relief coordinator."},
                    {"role": "user", "content": prompt}
                ]
                
                formatted_prompt = self.tokenizer.apply_chat_template(
                    conversation,
                    tokenize=False,
                    add_generation_prompt=True
                )
                
                inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
                
                with torch.no_grad():
                    outputs = self.peft_model.generate(
                        inputs.input_ids,
                        max_new_tokens=100,
                        temperature=0.7,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                response_only = response[len(formatted_prompt):].strip()
                
                print(f"NOTES Response: {response_only[:150]}...")
            
            logging.info("COMPLETED Model testing completed")
            print("COMPLETED Model testing completed successfully!")
            return True
            
        except Exception as e:
            logging.error(f"FAILED Model testing failed: {e}")
            print(f"FAILED Model testing failed: {e}")
            return False
    
    def run_complete_pipeline(self) -> bool:
        """Run the complete LoRA training pipeline"""
        logging.info("LAUNCH STARTING LORA EMERGENCY RELIEF TRAINING")
        print("LAUNCH Starting Memory-Efficient Emergency Relief AI Training")
        print("=" * 60)
        
        steps = [
            ("Loading Model and Tokenizer", self.load_model_and_tokenizer),
            ("Setting up LoRA", self.setup_lora),
            ("Preparing Dataset", self.prepare_dataset),
            ("Setting up Trainer", self.setup_trainer),
            ("Training Model", self.train),
            ("Testing Model", self.test_model)
        ]
        
        for step_name, step_func in steps:
            print(f"\nCHECKLIST {step_name}...")
            logging.info(f"PROCESSING {step_name}...")
            
            start_time = time.time()
            success = step_func()
            duration = time.time() - start_time
            
            if success:
                logging.info(f"COMPLETED {step_name} completed in {duration:.2f}s")
                print(f"COMPLETED {step_name} completed ({duration:.1f}s)")
            else:
                logging.error(f"FAILED {step_name} failed after {duration:.2f}s")
                print(f"FAILED {step_name} failed")
                return False
        
        print("\nSUCCESS EMERGENCY RELIEF AI TRAINING COMPLETED!")
        print("=" * 60)
        logging.info("SUCCESS LORA EMERGENCY RELIEF TRAINING COMPLETED!")
        
        return True

def main():
    """Main entry point"""
    config_path = "./config/emergency_relief_training_config.json"
    
    trainer = LoRAEmergencyTrainer(config_path)
    success = trainer.run_complete_pipeline()
    
    if success:
        print("\nSUCCESS Emergency Relief AI LoRA training completed successfully!")
        print(f"FOLDER Model saved to: {trainer.config['output_dir']}/emergency_relief_lora")
        print("LAUNCH Ready for deployment!")
        return 0
    else:
        print("\nFAILED Training failed. Check logs for details.")
        return 1

if __name__ == "__main__":
    exit(main())
