# GPT-OSS 20B Implementation Progress

This document tracks the detailed progress of implementing GPT-OSS 20B in the Vitalis application, including step-by-step logs, successes, challenges, and lessons learned.

## 📅 Implementation Timeline

### Phase 1: Initial Setup and Model Download

**Date**: 2025-09-09  
**Duration**: ~2 hours  
**Status**: ✅ Completed

### Phase 2: Model Loading and Testing

**Date**: 2025-09-09  
**Duration**: ~30 minutes  
**Status**: ⚠️ Partial Success with Issues

#### Step-by-Step Execution Log

##### 1. Environment Setup

```bash
# Virtual environment creation
python -m venv .venv
source .venv/bin/activate
```

**Result**: ✅ Success - Virtual environment created and activated

##### 2. Dependencies Installation

```bash
# Package installation (based on successful terminal log)
pip install transformers torch huggingface_hub tokenizers safetensors
pip install numpy pyyaml requests tqdm regex
pip install InquirerPy prompt-toolkit jinja2
```

**Successfully Installed Packages**:

- ✅ transformers-4.56.1
- ✅ torch-2.8.0
- ✅ huggingface_hub-0.34.4
- ✅ tokenizers-0.22.0
- ✅ safetensors-0.6.2
- ✅ numpy-2.3.3
- ✅ pyyaml-6.0.2
- ✅ requests-2.32.5
- ✅ InquirerPy-0.3.4
- ✅ prompt-toolkit-3.0.52
- ✅ jinja2-3.1.6
- ✅ And 15+ supporting packages

**Result**: ✅ Success - All packages installed without errors

##### 3. Hugging Face Authentication

```bash
hf auth login
```

**Process**:

1. Prompted for token input (input hidden for security)
2. Asked about git credential storage - chose 'n'
3. Token validated with "read" permission
4. Token saved to `/Users/sam/.cache/huggingface/stored_tokens`
5. Login successful with token name "Vitalis"

**Result**: ✅ Success - Authentication completed successfully

##### 4. Authentication Verification

```bash
# First attempt (incorrect command)
hf whoami
# Error: invalid choice: 'whoami'

# Correct command
huggingface-cli whoami
# Warning: 'huggingface-cli whoami' is deprecated. Use 'hf auth whoami' instead.
# user: Sam-T-G

# Modern command
hf auth whoami
# Sam-T-G
```

**Result**: ✅ Success - Authentication verified, user identified as "Sam-T-G"

##### 5. Model Directory Creation

```bash
mkdir -p models
```

**Result**: ✅ Success - Directory created successfully

##### 6. GPT-OSS 20B Model Download

```bash
huggingface-cli download openai/gpt-oss-20b \
  --local-dir ./models/gpt-oss-20b \
  --local-dir-use-symlinks False
```

**Download Process Details**:

**Files Downloaded** (18 total):

1. ✅ `chat_template.jinja` (16.7kB) - 66.2MB/s
2. ✅ `config.json` (1.81kB) - 19.0MB/s
3. ✅ `USAGE_POLICY` (200B) - 3.90MB/s
4. ✅ `generation_config.json` (177B) - 3.23MB/s
5. ✅ `README.md` (7.09kB) - 35.1MB/s
6. ✅ `.gitattributes` (1.57kB) - 36.4kB/s
7. ✅ `model.safetensors.index.json` (36.4kB) - 166MB/s
8. ✅ `original/config.json` (376B) - 5.63MB/s
9. ✅ `original/dtypes.json` (13.1kB) - 40.4MB/s
10. ✅ `LICENSE` (11.4kB) - 12.1MB/s
11. ✅ `tokenizer.json` (27.9M) - 7.57MB/s
12. ✅ `special_tokens_map.json` (98.0B) - 430kB/s
13. ✅ `tokenizer_config.json` (4.20kB) - 8.35MB/s
14. 🔄 `metal/model.bin` (13.8G) - 157kB/s (in progress)
15. 🔄 `model-00000-of-00002.safetensors` (4.79G) - 531kB/s (in progress)
16. 🔄 `model-00002-of-00002.safetensors` (4.17G) - 592kB/s (in progress)
17. 🔄 `model-00001-of-00002.safetensors` (4.80G) - 254kB/s (in progress)
18. 🔄 `original/model.safetensors` (13.8G) - 3.38MB/s (in progress)

**Download Performance Analysis**:

- **Small Files** (< 1MB): Very fast (35-166 MB/s)
- **Medium Files** (1-30MB): Good speed (7-8 MB/s)
- **Large Model Files** (> 1GB): Slow but steady (157kB/s - 3.38MB/s)

**Warnings Encountered**:

- ⚠️ `'huggingface-cli download' is deprecated. Use 'hf download' instead.`
- ⚠️ `Ignoring --local-dir-use-symlinks. Downloading to a local directory does not use symlinks anymore.`

**Result**: ✅ Success - All files downloaded successfully to `./models/gpt-oss-20b/`

#### Step-by-Step Execution Log - Phase 2

##### 7. Additional Dependencies Installation

```bash
# Install accelerate for device mapping and memory optimization
pip install accelerate
```

**Successfully Installed Packages**:

- ✅ accelerate-1.10.1
- ✅ psutil-7.0.0

**Result**: ✅ Success - Additional packages installed for model optimization

##### 8. Model Loading Script Creation

Created `scripts/hello_transformers.py` with the following configuration:

```python
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
import os

path = "./models/gpt-oss-20b"

tok = AutoTokenizer.from_pretrained(path, local_files_only=True)

model = AutoModelForCausalLM.from_pretrained(
    path,
    dtype="auto",              # new arg name (replaces torch_dtype)
    device_map="auto",         # needs 'accelerate' installed
    low_cpu_mem_usage=True,
    local_files_only=True
)

streamer = TextStreamer(tok)
prompt = "You are a cautious first-aid helper. An adult has a shallow forearm cut. Give brief, safe first-aid steps only."
ids = tok.apply_chat_template(
    [{"role":"user","content":prompt}],
    add_generation_prompt=True,
    return_tensors="pt"
).to(model.device)

_ = model.generate(ids, max_new_tokens=160, temperature=0.2, streamer=streamer)
```

**Result**: ✅ Success - Script created with proper configuration

##### 9. Model Loading Attempt

```bash
python scripts/hello_transformers.py
```

**Loading Process**:

1. **Quantization Warning**: `Using MXFP4 quantized models requires a GPU, we will default to dequantizing the model to bf16`
2. **Checkpoint Loading**: `Loading checkpoint shards: 100%|███████████████████████████████████████████████| 3/3 [00:13<00:00, 4.59s/it]`
3. **Memory Offloading**: `Some parameters are on the meta device because they were offloaded to the disk.`
4. **Attention Mask Warning**: `The attention mask is not set and cannot be inferred from input because pad token is same as eos token.`

**Result**: ⚠️ Partial Success - Model loaded but with warnings and eventual error

##### 10. Model Generation Attempt

The model began generating output:

```
<|start|>system<|message|>You are ChatGPT, a large language model trained by OpenAI.
Knowledge cutoff: 2024-06
Current date: 2025-09-09
Reasoning: medium
# Valid channels: analysis, commentary, final. Channel must be included for every message.<|end|><|start|>user<|message|>You are a cautious first-aid helper. An adult has a shallow forearm cut. Give brief, safe first-aid steps
```

**Result**: ❌ Error - Generation failed with KeyError

##### 11. Error Analysis

**Error Details**:

```
KeyError: 'model.layers.7.mlp.experts.gate_up_proj'
```

**Error Location**:

- File: `/Users/sam/Documents/repositories/Vitalis/.venv/lib/python3.13/site-packages/accelerate/utils/offload.py`
- Line 165: `weight_info = self.index[key]`
- Function: `__getitem__` in offload utility

**Error Context**:

- The error occurs during model generation when trying to access expert weights
- Specifically fails when accessing `model.layers.7.mlp.experts.gate_up_proj`
- This suggests an issue with the model's MoE (Mixture of Experts) architecture
- The error happens in the accelerate library's offloading mechanism

**Root Cause Analysis**:

1. **Model Architecture Issue**: GPT-OSS 20B uses MoE architecture with expert layers
2. **Weight Mapping Problem**: The accelerate library cannot find the expected weight key
3. **Offloading Conflict**: Model parameters are offloaded to disk but weight mapping is incomplete
4. **Quantization Impact**: MXFP4 quantization may have affected weight naming/structure

**Result**: ❌ Critical Error - Model generation completely fails

## 📊 Key Metrics and Observations

### Download Performance

| File Type       | Size Range | Speed Range        | Notes           |
| --------------- | ---------- | ------------------ | --------------- |
| Config Files    | < 1MB      | 35-166 MB/s        | Very fast       |
| Tokenizer Files | 1-30MB     | 7-8 MB/s           | Good speed      |
| Model Files     | > 1GB      | 157kB/s - 3.38MB/s | Slow but steady |

### Total Download Size

- **Total Model Size**: ~13.8GB
- **Additional Files**: ~28MB (config, tokenizer, etc.)
- **Total Download**: ~13.83GB

### Time Estimates

- **Small Files**: < 1 minute
- **Large Model Files**: 1-2 hours (depending on connection)
- **Total Time**: 1-2 hours

## 🎯 Successes

### ✅ Completed Successfully

1. **Environment Setup**: Virtual environment created and activated
2. **Dependencies**: All required packages installed without conflicts
3. **Authentication**: Hugging Face authentication successful
4. **Model Download**: Complete model download to local directory
5. **File Organization**: All model files properly organized in `./models/gpt-oss-20b/`

### ✅ Key Achievements

- Successfully authenticated with Hugging Face using personal access token
- Downloaded complete GPT-OSS 20B model (13.8GB) without errors
- All configuration and tokenizer files downloaded successfully
- Model ready for integration testing

## 🚧 Challenges Encountered

### ⚠️ Minor Issues

1. **Deprecated CLI Commands**: Some commands show deprecation warnings but still work
2. **Slow Download Speeds**: Large model files download slowly (expected behavior)
3. **Command Confusion**: Initial attempt to use `hf whoami` instead of `hf auth whoami`

### ❌ Critical Issues

1. **MXFP4 Quantization Error**: Model requires GPU for quantized weights, defaults to bf16 dequantization
2. **MoE Architecture Compatibility**: KeyError when accessing expert layer weights (`model.layers.7.mlp.experts.gate_up_proj`)
3. **Accelerate Offloading Issue**: Weight mapping fails in accelerate library's offload mechanism
4. **Model Generation Failure**: Complete failure during text generation due to missing weight keys

### 🔧 Solutions Applied

1. **Deprecation Warnings**: Ignored warnings as commands still function correctly
2. **Slow Downloads**: Accepted as normal behavior for large model files
3. **Command Issues**: Used correct modern commands after initial confusion

### 🔧 Solutions Needed (Critical Issues)

1. **GPU Requirement**: Need GPU access for proper MXFP4 quantization support
2. **MoE Compatibility**: Investigate alternative loading methods for MoE models
3. **Accelerate Configuration**: Adjust accelerate settings or disable offloading
4. **Model Loading Strategy**: Consider different loading parameters or model variants

## 📝 Lessons Learned

### Technical Insights

1. **Model Size Impact**: GPT-OSS 20B is a large model (13.8GB) requiring significant storage
2. **Download Performance**: Different file types have vastly different download speeds
3. **CLI Evolution**: Hugging Face CLI commands are evolving (deprecation warnings indicate this)
4. **Authentication**: Personal access tokens work reliably for model access
5. **MoE Architecture Complexity**: GPT-OSS 20B uses Mixture of Experts architecture which adds complexity
6. **Quantization Requirements**: MXFP4 quantization requires GPU support, falls back to bf16 on CPU
7. **Accelerate Library Issues**: Current accelerate version has compatibility issues with this MoE model
8. **Memory Management**: Model offloading to disk works but weight mapping fails

### Process Improvements

1. **Documentation**: Need to document expected download times for large models
2. **Monitoring**: Progress bars are helpful for tracking long downloads
3. **Error Handling**: Deprecation warnings should be documented as expected behavior

## 🔄 Next Steps

### Immediate Actions

- [x] Test model loading and basic inference (FAILED - KeyError)
- [ ] Investigate MoE model loading alternatives
- [ ] Test with GPU access for proper quantization
- [ ] Try different accelerate configurations
- [ ] Document hardware requirements based on model size
- [ ] Create integration tests for model functionality
- [ ] Set up proper configuration for the Vitalis application

### Future Considerations

- [ ] Implement model quantization to reduce memory requirements
- [ ] Set up automated model update pipeline
- [ ] Create performance benchmarks
- [ ] Develop deployment strategy for production

## 📚 Resources Used

### Commands Executed

```bash
# Environment setup
python -m venv .venv
source .venv/bin/activate

# Package installation
pip install transformers torch huggingface_hub tokenizers safetensors numpy pyyaml requests tqdm regex InquirerPy prompt-toolkit jinja2

# Authentication
hf auth login

# Verification
hf auth whoami

# Model download
mkdir -p models
huggingface-cli download openai/gpt-oss-20b --local-dir ./models/gpt-oss-20b --local-dir-use-symlinks False
```

### Files Created

- `./models/gpt-oss-20b/` - Complete model directory with all files
- Virtual environment in `.venv/`
- Hugging Face token cache in `/Users/sam/.cache/huggingface/`

---

_This implementation log will be updated as the GPT-OSS 20B integration progresses._
