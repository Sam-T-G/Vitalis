# GPT-OSS 20B Setup Guide

This guide provides step-by-step instructions for setting up GPT-OSS 20B in the Vitalis application environment, updated with the latest best practices and compatibility information.

## Prerequisites

### System Requirements

- **OS**: macOS 10.15+, Linux (Ubuntu 20.04+), or Windows 10+
- **RAM**: Minimum 16GB (32GB+ recommended for optimal performance)
- **Storage**: At least 20GB free space (model is ~13.8GB)
- **GPU**: Optional but recommended for MXFP4 quantization (NVIDIA GPU with 16GB+ VRAM)
- **CPU**: Multi-core processor (8+ cores recommended)

### Software Dependencies

- [ ] Python 3.8+ (3.11+ recommended)
- [ ] pip (latest version)
- [ ] Git (for version control)
- [ ] Hugging Face CLI (installed via pip)

### Accounts & Credentials

- [ ] Hugging Face account with access to GPT-OSS 20B model
- [ ] Hugging Face personal access token (read permissions)

## Installation Steps

### Step 1: Environment Setup

#### Virtual Environment Creation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### Dependencies Installation

```bash
# Install core ML packages (latest versions as of 2025)
pip install transformers>=4.56.0 torch>=2.0.0 huggingface_hub>=0.34.0
pip install tokenizers>=0.22.0 safetensors>=0.6.0 accelerate>=1.10.0

# Install additional utilities
pip install numpy pyyaml requests tqdm regex
pip install InquirerPy prompt-toolkit jinja2

# Optional: Install for better performance
pip install bitsandbytes  # For quantization support
pip install flash-attn     # For faster attention (requires CUDA)
```

**Recommended Package Versions** (tested and verified):

- transformers-4.56.1+
- torch-2.8.0+
- huggingface_hub-0.34.4+
- tokenizers-0.22.0+
- safetensors-0.6.2+
- accelerate-1.10.1+
- numpy-2.3.3+
- pyyaml-6.0.2+
- requests-2.32.5+

### Step 2: Model Download

#### Prerequisites

- Hugging Face account with access to GPT-OSS 20B model
- Hugging Face CLI installed (`pip install huggingface_hub`)
- Sufficient disk space (at least 15GB free)

#### Authentication

```bash
# Authenticate with Hugging Face
hf auth login
# Enter your token when prompted (generated from https://huggingface.co/settings/tokens)
# Choose 'n' when asked about git credential storage
```

#### Download Process

```bash
# Create models directory
mkdir -p models

# Modern approach (recommended)
hf download openai/gpt-oss-20b --local-dir ./models/gpt-oss-20b

# Alternative: Legacy command (still works but deprecated)
huggingface-cli download openai/gpt-oss-20b \
  --local-dir ./models/gpt-oss-20b \
  --local-dir-use-symlinks False
```

**Download Notes**:

- Use `hf download` (modern) instead of `huggingface-cli download` (deprecated)
- The `--local-dir-use-symlinks False` flag is deprecated but still functional
- Total download size: ~13.8GB (expect 1-2 hours depending on connection)
- Large model files download slowly (157kB/s - 3.38MB/s) - this is normal

### Step 3: Model Loading and Testing

#### Basic Model Loading Test

Create a test script to verify model loading:

```bash
# Create test script
cat > test_model_loading.py << 'EOF'
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Load model and tokenizer
model_path = "./models/gpt-oss-20b"
tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)

# Try different loading strategies for MoE compatibility
try:
    # Strategy 1: With device_map (may cause MoE issues)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.float16,
        device_map="auto",
        low_cpu_mem_usage=True,
        local_files_only=True
    )
    print("Model loaded successfully with device_map='auto'")
except Exception as e:
    print(f"Strategy 1 failed: {e}")

    try:
        # Strategy 2: Without device_map (CPU only)
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            local_files_only=True
        )
        print("Model loaded successfully without device_map")
    except Exception as e2:
        print(f"Strategy 2 failed: {e2}")
        print("Please check the troubleshooting section for MoE compatibility issues")
EOF

# Run the test
python test_model_loading.py
```

#### Alternative Loading Methods

If the standard loading fails due to MoE architecture issues, try these alternatives:

```python
# Alternative 1: Use pipeline (recommended for GPT-OSS)
from transformers import pipeline
import torch

model_id = "./models/gpt-oss-20b"
pipe = pipeline(
    "text-generation",
    model=model_id,
    torch_dtype=torch.float16,
    device_map="auto" if torch.cuda.is_available() else None,
)

# Test generation
messages = [{"role": "user", "content": "Hello, how are you?"}]
outputs = pipe(messages, max_new_tokens=50)
print(outputs[0]["generated_text"][-1])
```

### Step 4: Alternative Setup Methods

#### Option A: Using vLLM (Recommended for Production)

```bash
# Install vLLM with GPT-OSS support
pip install vllm==0.10.1+gptoss \
    --extra-index-url https://wheels.vllm.ai/gpt-oss/ \
    --extra-index-url https://download.pytorch.org/whl/nightly/cu128

# Start vLLM server
vllm serve openai/gpt-oss-20b --port 8000
```

#### Option B: Using Ollama (For Local Development)

```bash
# Install Ollama (if not already installed)
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh

# Pull and run GPT-OSS 20B
ollama pull gpt-oss:20b
ollama run gpt-oss:20b
```

#### Option C: Using LM Studio

```bash
# Install LM Studio from https://lmstudio.ai/
# Then download the model
lms get openai/gpt-oss-20b
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# GPT-OSS Configuration
GPT_OSS_MODEL_PATH=/path/to/model
GPT_OSS_API_KEY=your_api_key_here
GPT_OSS_MAX_TOKENS=2048
GPT_OSS_TEMPERATURE=0.7

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/vitalis

# Security
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1

# Logging
LOG_LEVEL=INFO
LOG_FILE=/path/to/logs/gpt-oss.log
```

### Model Configuration (config/gpt-oss.yaml)

```yaml
model:
  name: "gpt-oss-20b"
  path: "/path/to/model"
  max_tokens: 2048
  temperature: 0.7
  top_p: 0.9
  frequency_penalty: 0.0
  presence_penalty: 0.0

api:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  timeout: 30

cache:
  enabled: true
  ttl: 3600
  max_size: 1000

monitoring:
  enabled: true
  metrics_endpoint: "/metrics"
  health_check: "/health"
```

## Development Setup

### Local Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run linting
flake8 src/
black src/

# Start development server with hot reload
python manage.py runserver --reload
```

### Docker Development

```bash
# Build development image
docker build -f Dockerfile.dev -t vitalis-gpt-oss:dev .

# Run development container
docker run -p 8000:8000 -v $(pwd):/app vitalis-gpt-oss:dev
```

## TEST Testing Setup

### Unit Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_gpt_oss.py

# Run with coverage
python -m pytest --cov=src tests/
```

### Integration Tests

```bash
# Start test database
docker run -d --name test-db -e POSTGRES_PASSWORD=test postgres:13

# Run integration tests
python -m pytest tests/integration/
```

### Load Testing

```bash
# Install load testing tools
pip install locust

# Run load tests
locust -f tests/load_test.py --host=http://localhost:8000
```

## Monitoring Setup

### Application Monitoring

```bash
# Install monitoring tools
pip install prometheus-client

# Start monitoring
python scripts/start_monitoring.py
```

### Log Aggregation

```bash
# Configure log shipping
# Add to your logging configuration
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/var/log/vitalis/gpt-oss.log',
        },
    },
}
```

##  Security Configuration

### API Security

```python
# Add to your settings
API_SECURITY = {
    'rate_limiting': {
        'enabled': True,
        'requests_per_minute': 100,
    },
    'authentication': {
        'required': True,
        'token_expiry': 3600,
    },
    'cors': {
        'allowed_origins': ['https://yourdomain.com'],
        'allowed_methods': ['GET', 'POST'],
    }
}
```

### Data Protection

```bash
# Encrypt sensitive data
python scripts/encrypt_config.py --input config/sensitive.yaml --output config/sensitive.enc

# Set proper file permissions
chmod 600 config/sensitive.enc
chmod 700 config/
```

## ALERT Troubleshooting

### Common Setup Issues

#### Issue: Model Download Fails

**Symptoms**: Download script fails or times out  
**Solutions**:

1. Check internet connection
2. Verify storage space (need at least 15GB free)
3. Try downloading in smaller chunks
4. Use alternative download mirror

#### Issue: Slow Download Speeds

**Symptoms**: Very slow download speeds (e.g., 157kB/s for large files)  
**Solutions**:

1. **Expected Behavior**: Large model files (13.8GB total) will download slowly
2. **File-Specific Speeds**: Different files download at different speeds:
   - Small config files: 35-66 MB/s
   - Large model files: 157kB/s - 3.38MB/s
   - Tokenizer files: 7.57MB/s
3. **Patience Required**: Total download time can be 1-2 hours depending on connection
4. **Monitor Progress**: Use the progress bars shown in terminal to track download status

#### Issue: Deprecated CLI Warnings

**Symptoms**: Warning messages about deprecated commands  
**Solutions**:

1. **Warning**: `'huggingface-cli download' is deprecated. Use 'hf download' instead.`
   - **Action**: Command still works, but consider using `hf download` for future downloads
2. **Warning**: `'huggingface-cli whoami' is deprecated. Use 'hf auth whoami' instead.`
   - **Action**: Use `hf auth whoami` to check authentication status
3. **Warning**: `Ignoring --local-dir-use-symlinks. Downloading to a local directory does not use symlinks anymore.`
   - **Action**: This is just informational, download will proceed normally

#### Issue: Configuration Errors

**Symptoms**: Service fails to start with config errors  
**Solutions**:

1. Validate YAML syntax
2. Check environment variables
3. Verify file paths exist
4. Review log files for specific errors

#### Issue: Memory Issues

**Symptoms**: Out of memory errors during startup  
**Solutions**:

1. Increase system RAM
2. Reduce model batch size
3. Enable model quantization
4. Use CPU-only mode for testing

#### Issue: MXFP4 Quantization Error

**Symptoms**: Warning message "Using MXFP4 quantized models requires a GPU, we will default to dequantizing the model to bf16"  
**Solutions**:

1. **Expected Behavior**: This is normal when running on CPU without GPU
2. **GPU Access**: Use GPU-enabled environment for proper MXFP4 quantization
3. **Accept Fallback**: The bf16 dequantization works but may impact performance
4. **Alternative**: Consider using different model variants or quantization methods

#### Issue: MoE Architecture KeyError

**Symptoms**: `KeyError: 'model.layers.X.mlp.experts.gate_up_proj'` during generation  
**Root Cause**: GPT-OSS 20B uses Mixture of Experts (MoE) architecture with 32 local experts and 4 experts per token  
**Solutions**:

1. **Use Pipeline Approach** (Recommended):

   ```python
   from transformers import pipeline
   pipe = pipeline("text-generation", model="./models/gpt-oss-20b")
   ```

2. **Disable Device Mapping**:

   ```python
   model = AutoModelForCausalLM.from_pretrained(
       model_path,
       torch_dtype=torch.float16,
       low_cpu_mem_usage=True,
       local_files_only=True
       # Remove device_map="auto"
   )
   ```

3. **Use vLLM** (Best for production):

   ```bash
   pip install vllm==0.10.1+gptoss --extra-index-url https://wheels.vllm.ai/gpt-oss/
   vllm serve openai/gpt-oss-20b
   ```

4. **Use Ollama** (Easiest for local development):
   ```bash
   ollama pull gpt-oss:20b
   ollama run gpt-oss:20b
   ```

#### Issue: Model Generation Failure

**Symptoms**: Model loads successfully but fails during text generation with KeyError  
**Solutions**:

1. **Update to Latest Versions**: Ensure you have the latest transformers and accelerate
2. **Use Alternative Loading**: Try the pipeline approach instead of direct model loading
3. **Check GPU Compatibility**: MXFP4 quantization requires GPU for optimal performance
4. **Consider Model Variants**: The model has both quantized and original versions available

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export DEBUG=True

# Start with verbose output
python manage.py runserver --verbosity=2
```

## Verification

### Health Checks

```bash
# Check service health
curl http://localhost:8000/health

# Check model status
curl http://localhost:8000/api/v1/model/status

# Test basic functionality
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, world!", "max_tokens": 50}'
```

### Performance Verification

```bash
# Run performance tests
python scripts/performance_test.py

# Check resource usage
python scripts/resource_monitor.py
```

## Next Steps

After successful setup:

1. [ ] **Test Model Functionality**: Run the test script to verify model loading and generation
2. [ ] **Choose Integration Method**: Decide between vLLM, Ollama, or direct transformers integration
3. [ ] **Set Up Production Environment**: Configure for your specific use case (GPU requirements, memory optimization)
4. [ ] **Review the [Architecture Guide](architecture-guide.md)**
5. [ ] **Read the [API Documentation](api-documentation.md)**
6. [ ] **Explore [Usage Examples](usage-examples.md)**
7. [ ] **Set up [Monitoring and Alerting](monitoring-setup.md)**

### Recommended Next Actions Based on Your Current Status

Since you've already downloaded the model and encountered MoE compatibility issues:

1. **Immediate**: Try the pipeline approach or vLLM setup
2. **Short-term**: Set up Ollama for easier local development
3. **Medium-term**: Configure production deployment with vLLM
4. **Long-term**: Integrate with your Vitalis application architecture

## Getting Help

### Documentation

- [Official GPT-OSS Documentation](link)
- [API Reference](link)
- [Troubleshooting Guide](troubleshooting.md)

### Support Channels

- **Internal Slack**: #gpt-oss-support
- **GitHub Issues**: [Repository Issues](link)
- **Team Contact**: [Contact Information]

---

_Last updated: 2025-09-09_  
_Setup verified by: Sam_  
_Status: Updated with latest GPT-OSS 20B compatibility information and MoE architecture solutions_
