# GPT-OSS 20B Setup Guide

This guide provides step-by-step instructions for setting up GPT-OSS 20B in the Vitalis application environment.

## 📋 Prerequisites

### System Requirements

- **OS**: [Linux/macOS/Windows version]
- **RAM**: [Minimum RAM requirement]
- **Storage**: [Minimum storage requirement]
- **GPU**: [GPU requirements if applicable]
- **CPU**: [CPU requirements]

### Software Dependencies

- [ ] Python [version]
- [ ] Node.js [version]
- [ ] Docker [version]
- [ ] [Other dependency 1]
- [ ] [Other dependency 2]

### Accounts & Credentials

- [ ] [Service account 1]
- [ ] [API key 1]
- [ ] [Access token 1]

## 🚀 Installation Steps

### Step 1: Environment Setup

#### Virtual Environment Creation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### Dependencies Installation

```bash
# Install required packages (based on successful installation log)
pip install transformers torch huggingface_hub tokenizers safetensors
pip install numpy pyyaml requests tqdm regex
pip install InquirerPy prompt-toolkit jinja2
```

**Successfully Installed Packages**:

- transformers-4.56.1
- torch-2.8.0
- huggingface_hub-0.34.4
- tokenizers-0.22.0
- safetensors-0.6.2
- numpy-2.3.3
- pyyaml-6.0.2
- requests-2.32.5
- And other supporting packages

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

# Download GPT-OSS 20B model
huggingface-cli download openai/gpt-oss-20b \
  --local-dir ./models/gpt-oss-20b \
  --local-dir-use-symlinks False
```

**Note**: The `--local-dir-use-symlinks False` flag is deprecated but still works. The CLI will show a warning but continue with the download.

### Step 3: Configuration

```bash
# Copy configuration template
cp config/gpt-oss.template.yaml config/gpt-oss.yaml

# Edit configuration file
nano config/gpt-oss.yaml
```

### Step 4: Database Setup

```bash
# Run database migrations
python manage.py migrate

# Create initial data
python manage.py loaddata initial_data.json
```

### Step 5: Service Initialization

```bash
# Start the service
python manage.py runserver

# Or with Docker
docker-compose up -d
```

## ⚙️ Configuration

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

## 🔧 Development Setup

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

## 🧪 Testing Setup

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

## 📊 Monitoring Setup

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

## 🔒 Security Configuration

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

## 🚨 Troubleshooting

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

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export DEBUG=True

# Start with verbose output
python manage.py runserver --verbosity=2
```

## ✅ Verification

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

## 📚 Next Steps

After successful setup:

1. [ ] Review the [Architecture Guide](architecture-guide.md)
2. [ ] Read the [API Documentation](api-documentation.md)
3. [ ] Explore [Usage Examples](usage-examples.md)
4. [ ] Set up [Monitoring and Alerting](monitoring-setup.md)

## 🆘 Getting Help

### Documentation

- [Official GPT-OSS Documentation](link)
- [API Reference](link)
- [Troubleshooting Guide](troubleshooting.md)

### Support Channels

- **Internal Slack**: #gpt-oss-support
- **GitHub Issues**: [Repository Issues](link)
- **Team Contact**: [Contact Information]

---

_Last updated: [Date]_  
_Setup verified by: [Name]_
