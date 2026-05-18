# 🚀 Quick Start Guide

Get up and running with the Recursive Agentic AI Platform in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Your API Key

Choose one of these methods:

### Method A: Environment Variable (Recommended)

```bash
export OPENAI_API_KEY="sk-your-actual-api-key"
```

### Method B: Create .env File

```bash
cp .env.example .env
# Edit .env and add your API key
```

### Method C: Pass Directly in Code

```python
platform = AgenticPlatform(api_key="sk-your-key", ...)
```

## Step 3: Run Your First Agent

### Option 1: Quick Test (No API Key Needed)

```python
from agentic_platform import solve

result = solve("Write a function to calculate fibonacci numbers", use_mock=True)
print(result['result'])
```

### Option 2: Use Real API

```python
from agentic_platform import solve

result = solve(
    "Create a REST API for a todo app",
    requirements=["Use FastAPI", "Add JWT auth"],
    api_key="your-key",
    provider="openai"
)
print(result['result'])
```

### Option 3: Use the Web Interface

```bash
python start_web_interface.py
# Open http://localhost:8000 in your browser
```

## Step 4: Explore Examples

```bash
# Run all examples
python examples.py

# Run specific example
python -c "from examples import example_basic_usage; example_basic_usage()"
```

## Step 5: Run Tests

```bash
pytest tests.py -v
```

## Common Issues

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Authentication failed"
- Check your API key is correct
- Ensure no extra spaces or quotes
- Verify you have credits in your account

### "Port 8000 already in use"
```bash
lsof -i :8000
kill -9 <PID>
```

## Next Steps

- 📖 Read the full [README.md](README.md)
- 🎨 Explore the [Web Interface Guide](WEB_INTERFACE_GUIDE.md)
- 🤖 Check out [DeepSeek Usage Guide](DEEPSEEK_USAGE.md)
- ⚙️ Customize settings in [config.yaml](config.yaml)

---

**Need Help?** Check the troubleshooting section in README.md or open an issue.
