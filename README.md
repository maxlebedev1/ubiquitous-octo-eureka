# Recursive Agentic AI Platform

A powerful, recursive multi-agent system that breaks down complex problems into manageable sub-tasks, evaluates outcomes, and iteratively improves until success.

## Features

- **Recursive Task Decomposition**: Breaks goals into steps, each handled by specialized sub-agents
- **Adaptive Depth**: Recursively decomposes until tasks are simple enough for reliable LLM execution
- **Outcome Evaluation**: Each task is evaluated against expected requirements
- **Self-Correction**: Failed tasks are automatically fixed or restarted (up to 5 attempts)
- **Token Efficiency**: Only creates necessary agents and maintains focused context
- **Agent Lifecycle Management**: Agents are deleted after successful completion
- **Multi-Provider Support**: Works with OpenAI, DeepSeek, and any OpenAI-compatible API

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage with OpenAI

```python
from agentic_platform import AgenticPlatform

# Initialize the platform
platform = AgenticPlatform(
    api_key="your-api-key",
    model="gpt-4",
    max_depth=3,  # Maximum recursion depth
    max_retries=5  # Maximum retry attempts per task
)

# Execute a complex goal
result = platform.execute("Build a complete web scraper for e-commerce sites")
print(result)
```

### Using DeepSeek

```python
from agentic_platform import AgenticPlatform

# Initialize with DeepSeek
platform = AgenticPlatform(
    api_key="your-deepseek-api-key",
    model="deepseek-chat",  # or "deepseek-coder" for coding tasks
    provider="deepseek",  # Specify DeepSeek as the provider
    max_depth=3,
    max_retries=5
)

# Execute a goal
result = platform.execute("Write a Python function to implement merge sort")
print(result)
```

### Using Custom Endpoints (Ollama, Local LLMs, etc.)

```python
from agentic_platform import AgenticPlatform

# Initialize with custom endpoint (e.g., Ollama)
platform = AgenticPlatform(
    api_key="ollama",  # Not required for local servers
    model="llama3",  # Your preferred model
    base_url="http://localhost:11434/v1",  # Custom endpoint
    provider="custom",  # Use custom provider for OpenAI-compatible APIs
    max_depth=2,
    max_retries=3
)

# Execute a goal
result = platform.execute("Explain quantum computing")
print(result)
```

### Quick Start with Mock (Testing)

```python
from agentic_platform import solve

# Solve a problem with mock LLM (for testing)
result = solve("Create a web scraper", use_mock=True)
print(result)

# Solve with real API
result = solve(
    "Build a REST API for user management",
    requirements=["Use FastAPI", "Add JWT auth"],
    api_key="your-api-key",
    provider="openai",  # or "deepseek" or "custom"
    max_depth=3,
    max_retries=5
)
```

## Architecture

```
Goal
├── Step 1 → Agent 1
│   ├── Sub-step 1.1 → Sub-Agent 1.1
│   └── Sub-step 1.2 → Sub-Agent 1.2
├── Step 2 → Agent 2
│   └── ...
└── Step 3 → Agent 3
    └── ...
```

## Configuration

Edit `config.yaml` to customize:
- Model parameters
- Recursion depth
- Retry limits
- Token budgets

## Supported Providers

| Provider | Description | Default Base URL |
|----------|-------------|------------------|
| `openai` | OpenAI GPT models | https://api.openai.com/v1 |
| `deepseek` | DeepSeek V4 and other models | https://api.deepseek.com/v1 |
| `custom` | Any OpenAI-compatible API | User-specified |

### Examples of Custom Endpoints

- **Ollama**: `http://localhost:11434/v1`
- **LM Studio**: `http://localhost:1234/v1`
- **Azure OpenAI**: `https://YOUR_RESOURCE.openai.azure.com/openai/deployments/YOUR_DEPLOYMENT`
- **vLLM**: `http://localhost:8000/v1`

## Environment Variables

You can set API keys via environment variables:

```bash
export OPENAI_API_KEY="your-openai-key"
export DEEPSEEK_API_KEY="your-deepseek-key"
```

Then use in code:

```python
import os

platform = AgenticPlatform(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    provider="deepseek"
)
```

## Running Examples

```bash
# Run basic examples with mock LLM
python examples.py

# Run DeepSeek example (requires API key)
export DEEPSEEK_API_KEY="your-key"
python -c "from examples import example_deepseek; example_deepseek()"
```

