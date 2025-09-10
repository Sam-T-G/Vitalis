#!/usr/bin/env python3
"""
Training Pipeline Validation Script
Validates that all components are ready for emergency relief AI training
"""

import os
import sys
import json
import logging
from pathlib import Path
import importlib.util

def check_python_environment():
    """Check Python environment and dependencies"""
    print(" Checking Python Environment...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor >= 9:
        print(f"COMPLETED Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"FAILED Python version {python_version.major}.{python_version.minor} too old (need 3.9+)")
        return False
    
    # Check required packages
    required_packages = {
        'torch': '2.0.0',
        'transformers': '4.30.0',
        'accelerate': '0.20.0',
        'psutil': '5.0.0',
        'flask': '2.0.0'
    }
    
    missing_packages = []
    
    for package, min_version in required_packages.items():
        try:
            imported = importlib.import_module(package)
            version = getattr(imported, '__version__', 'unknown')
            print(f"COMPLETED {package} {version}")
        except ImportError:
            print(f"FAILED {package} not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nIDEA Install missing packages: pip install {' '.join(missing_packages)}")
        return False
    
    # Check Apple Silicon MPS
    try:
        import torch
        if torch.backends.mps.is_available():
            print("COMPLETED Apple Silicon MPS available")
        else:
            print("WARNING  MPS not available (will use CPU)")
    except:
        pass
    
    return True

def check_model_files():
    """Check that GPT-OSS 20B model files are present"""
    print("\n Checking Model Files...")
    
    model_path = Path("./models/gpt-oss-20b")
    
    if not model_path.exists():
        print(f"FAILED Model directory not found: {model_path}")
        return False
    
    required_files = [
        "config.json",
        "tokenizer.json",
        "tokenizer_config.json",
        "special_tokens_map.json"
    ]
    
    # Check for model safetensors files
    safetensors_files = list(model_path.glob("*.safetensors"))
    if not safetensors_files:
        print("FAILED No .safetensors model files found")
        return False
    
    print(f"COMPLETED Found {len(safetensors_files)} model files")
    
    for file in required_files:
        file_path = model_path / file
        if file_path.exists():
            print(f"COMPLETED {file}")
        else:
            print(f"FAILED Missing: {file}")
            return False
    
    # Check total model size
    total_size = sum(f.stat().st_size for f in model_path.rglob("*") if f.is_file())
    total_size_gb = total_size / (1024**3)
    print(f"METRICS Total model size: {total_size_gb:.1f}GB")
    
    if total_size_gb < 5:
        print("WARNING  Model seems unusually small")
    
    return True

def check_training_data():
    """Check training data files"""
    print("\nLIBRARY Checking Training Data...")
    
    data_file = Path("./data/ENHANCED_EMERGENCY_RELIEF_TRAINING_DATA.json")
    
    if not data_file.exists():
        print(f"FAILED Training data not found: {data_file}")
        return False
    
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        training_examples = data.get('training_data', [])
        metadata = data.get('metadata', {})
        
        print(f"COMPLETED Training data loaded")
        print(f"METRICS Examples: {len(training_examples)}")
        print(f"METRICS Categories: {len(metadata.get('categories', []))}")
        
        # Check data structure
        if training_examples:
            example = training_examples[0]
            required_keys = ['instruction', 'response']
            
            for key in required_keys:
                if key in example:
                    print(f"COMPLETED Example structure: {key}")
                else:
                    print(f"FAILED Missing key in examples: {key}")
                    return False
        
        # Estimate training data quality
        avg_instruction_length = sum(len(ex.get('instruction', '')) for ex in training_examples[:10]) / min(10, len(training_examples))
        avg_response_length = sum(len(ex.get('response', '')) for ex in training_examples[:10]) / min(10, len(training_examples))
        
        print(f"METRICS Avg instruction length: {avg_instruction_length:.0f} chars")
        print(f"METRICS Avg response length: {avg_response_length:.0f} chars")
        
        if avg_instruction_length < 20 or avg_response_length < 50:
            print("WARNING  Training examples seem short")
        
        return True
        
    except json.JSONDecodeError:
        print("FAILED Training data is not valid JSON")
        return False
    except Exception as e:
        print(f"FAILED Error checking training data: {e}")
        return False

def check_configuration():
    """Check training configuration"""
    print("\nSETTINGS  Checking Configuration...")
    
    config_file = Path("./config/emergency_relief_training_config.json")
    
    if not config_file.exists():
        print(f"FAILED Config file not found: {config_file}")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        print("COMPLETED Configuration loaded")
        
        # Check key parameters
        key_params = {
            'model_path': str,
            'data_path': str,
            'output_dir': str,
            'num_epochs': int,
            'batch_size': int,
            'learning_rate': float
        }
        
        for param, expected_type in key_params.items():
            if param in config:
                value = config[param]
                if isinstance(value, expected_type):
                    print(f"COMPLETED {param}: {value}")
                else:
                    print(f"WARNING  {param}: {value} (unexpected type)")
            else:
                print(f"FAILED Missing parameter: {param}")
                return False
        
        # Validate paths
        model_path = Path(config['model_path'])
        data_path = Path(config['data_path'])
        
        if not model_path.exists():
            print(f"FAILED Model path in config doesn't exist: {model_path}")
            return False
        
        if not data_path.exists():
            print(f"FAILED Data path in config doesn't exist: {data_path}")
            return False
        
        return True
        
    except json.JSONDecodeError:
        print("FAILED Configuration is not valid JSON")
        return False
    except Exception as e:
        print(f"FAILED Error checking configuration: {e}")
        return False

def check_system_resources():
    """Check system resources"""
    print("\nLAPTOP Checking System Resources...")
    
    try:
        import psutil
        
        # Memory
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        memory_available_gb = memory.available / (1024**3)
        
        print(f" Total RAM: {memory_gb:.1f}GB")
        print(f" Available RAM: {memory_available_gb:.1f}GB")
        
        if memory_gb < 16:
            print("WARNING  Less than 16GB RAM - training may be slow")
        elif memory_gb >= 24:
            print("COMPLETED Excellent RAM for training")
        
        # Disk space
        disk = psutil.disk_usage('.')
        disk_free_gb = disk.free / (1024**3)
        
        print(f"SAVE Free disk space: {disk_free_gb:.1f}GB")
        
        if disk_free_gb < 20:
            print("WARNING  Low disk space - need at least 20GB for training")
        
        # CPU
        cpu_count = psutil.cpu_count()
        print(f" CPU cores: {cpu_count}")
        
        return memory_gb >= 8 and disk_free_gb >= 10
        
    except ImportError:
        print("WARNING  Cannot check system resources (psutil not available)")
        return True

def check_output_directories():
    """Check and create output directories"""
    print("\nFOLDER Checking Output Directories...")
    
    directories = [
        "./models/emergency_relief_fine_tuned",
        "./models/emergency_relief_fine_tuned/logs",
        "./src/vitalis/training"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        if dir_path.exists():
            print(f"COMPLETED {directory}")
        else:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"COMPLETED Created: {directory}")
            except Exception as e:
                print(f"FAILED Cannot create: {directory} - {e}")
                return False
    
    return True

def check_training_scripts():
    """Check that training scripts are present and valid"""
    print("\n Checking Training Scripts...")
    
    scripts = [
        "./src/vitalis/training/emergency_relief_trainer.py",
        "./scripts/train_emergency_relief_ai.py",
        "./scripts/test_emergency_relief_model.py"
    ]
    
    for script in scripts:
        script_path = Path(script)
        if script_path.exists():
            print(f"COMPLETED {script}")
            
            # Basic syntax check
            try:
                with open(script_path, 'r') as f:
                    content = f.read()
                
                compile(content, script, 'exec')
                print(f"   COMPLETED Syntax valid")
                
            except SyntaxError as e:
                print(f"   FAILED Syntax error: {e}")
                return False
            except Exception as e:
                print(f"   WARNING  Cannot validate: {e}")
        else:
            print(f"FAILED Missing: {script}")
            return False
    
    return True

def main():
    """Main validation function"""
    print("SEARCH EMERGENCY RELIEF AI TRAINING PIPELINE VALIDATION")
    print("=" * 60)
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"FOLDER Working directory: {os.getcwd()}")
    
    # Run all checks
    checks = [
        ("Python Environment", check_python_environment),
        ("Model Files", check_model_files),
        ("Training Data", check_training_data),
        ("Configuration", check_configuration),
        ("System Resources", check_system_resources),
        ("Output Directories", check_output_directories),
        ("Training Scripts", check_training_scripts)
    ]
    
    passed_checks = 0
    total_checks = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n{'='*20} {check_name} {'='*20}")
        
        try:
            if check_func():
                print(f"COMPLETED {check_name}: PASSED")
                passed_checks += 1
            else:
                print(f"FAILED {check_name}: FAILED")
        except Exception as e:
            print(f"FAILED {check_name}: ERROR - {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("METRICS VALIDATION SUMMARY")
    print("=" * 60)
    print(f"COMPLETED Passed: {passed_checks}/{total_checks}")
    print(f"FAILED Failed: {total_checks - passed_checks}/{total_checks}")
    
    if passed_checks == total_checks:
        print("\nSUCCESS ALL CHECKS PASSED!")
        print("LAUNCH Ready to start training!")
        print("\nCHECKLIST Next steps:")
        print("   1. Run: python scripts/train_emergency_relief_ai.py")
        print("   2. Wait for training to complete (1-3 hours)")
        print("   3. Test: python scripts/test_emergency_relief_model.py")
        print("   4. Deploy: python scripts/deploy_emergency_relief_api.py")
        return 0
    else:
        print(f"\nWARNING  {total_checks - passed_checks} checks failed")
        print("CONFIG Please fix the issues above before training")
        return 1

if __name__ == "__main__":
    exit(main())
