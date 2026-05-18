# 🤖 Recursive Agentic AI Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful, recursive multi-agent system that autonomously breaks down complex problems into manageable sub-tasks, evaluates outcomes, and iteratively improves until success.

## ✨ Key Features

- **🔄 Recursive Task Decomposition**: Intelligently breaks goals into steps, each handled by specialized sub-agents
- **🎯 Adaptive Depth**: Recursively decomposes until tasks are simple enough for reliable LLM execution
- **✅ Outcome Evaluation**: Each task is evaluated against expected requirements
- **🔧 Self-Correction**: Failed tasks automatically retry (configurable attempts)
- **⚡ Token Efficiency**: Creates only necessary agents with focused context
- **🧹 Agent Lifecycle Management**: Agents auto-cleanup after successful completion
- **🌐 Multi-Provider Support**: OpenAI, DeepSeek, Ollama, LM Studio, and any OpenAI-compatible API
- **🎨 Real-Time Web Interface**: Beautiful dashboard to visualize agent execution live

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage (5 Minutes)

```python
from agentic_platform import solve

# Solve a problem with mock (testing - no API key needed)
result = solve("Create a web scraper for e-commerce sites", use_mock=True)
print(result['result'])

# Solve with real API (OpenAI)
result = solve(
    "Build a REST API for user management",
    requirements=["Use FastAPI", "Add JWT authentication"],
    api_key="your-openai-key",
    provider="openai",
    model="gpt-4"
)
```

### Using the Web Interface

```bash
# Start the web server
python start_web_interface.py

# Open browser to http://localhost:8000
```

The web interface provides:
- 🌳 Real-time agent tree visualization
- 📊 Live statistics and progress tracking
- 📝 Event log showing every action
- ⚙️ Easy configuration of all parameters

## 📖 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Examples](#-usage-examples)
  - [OpenAI](#openai)
  - [DeepSeek](#deepseek)
  - [Custom Endpoints (Ollama, Local LLMs)](#custom-endpoints-ollama-local-llms)
  - [Web Interface](#web-interface)
- [Architecture](#-architecture)
- [Configuration](#-configuration)
- [API Reference](#-api-reference)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

## 🔧 Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Optional: Install for Specific Providers

**OpenAI:**
```bash
pip install openai>=1.0.0
```

**DeepSeek:** (uses OpenAI client)
```bash
pip install openai>=1.0.0
```

**Environment Variables (Recommended):**
```bash
export OPENAI_API_KEY="your-openai-key"
export DEEPSEEK_API_KEY="your-deepseek-key"
```

## 💡 Usage Examples

### OpenAI

```python
from agentic_platform import AgenticPlatform

platform = AgenticPlatform(
    api_key="your-api-key",  # or use os.getenv("OPENAI_API_KEY")
    model="gpt-4",
    max_depth=3,
    max_retries=5
)

result = platform.execute_sync(
    goal="Build a complete web scraper for e-commerce sites",
    requirements=[
        "Handle pagination",
        "Extract product details",
        "Save to CSV",
        "Include error handling"
    ]
)

print(f"Success: {result['success']}")
print(f"Result: {result['result']}")
```

### DeepSeek

```python
from agentic_platform import AgenticPlatform

platform = AgenticPlatform(
    api_key="your-deepseek-key",
    model="deepseek-chat",  # or "deepseek-v4-pro", "deepseek-coder"
    provider="deepseek",
    max_depth=3,
    max_retries=5
)

result = platform.execute_sync("Write a merge sort implementation in Python")
```

**Available DeepSeek Models:**

| Model | Best For |
|-------|----------|
| `deepseek-v4-pro` | Complex reasoning, advanced coding |
| `deepseek-chat` | General tasks, conversation |
| `deepseek-coder` | Code generation, debugging |
| `deepseek-v3` | Cost-effective general tasks |

### Custom Endpoints (Ollama, Local LLMs)

```python
from agentic_platform import AgenticPlatform

# Ollama example
platform = AgenticPlatform(
    api_key="ollama",  # Not required for local
    model="llama3",
    base_url="http://localhost:11434/v1",
    provider="custom",
    max_depth=2,
    max_retries=3
)

result = platform.execute_sync("Explain quantum computing")
```

**Supported Custom Endpoints:**

| Service | Base URL |
|---------|----------|
| Ollama | `http://localhost:11434/v1` |
| LM Studio | `http://localhost:1234/v1` |
| vLLM | `http://localhost:8000/v1` |
| Azure OpenAI | `https://YOUR_RESOURCE.openai.azure.com/openai/deployments/YOUR_DEPLOYMENT` |

### Web Interface

The platform includes a beautiful real-time web interface:

```bash
# Start the server
python start_web_interface.py

# Visit http://localhost:8000 in your browser
```

**Features:**
- 🌳 Visual agent tree showing hierarchy
- 📊 Live statistics (agents created, completed, failed)
- 📝 Real-time event log
- 🎛️ Easy configuration of all parameters
- 🎨 Beautiful, responsive design

## 🏗️ Architecture

The platform uses a recursive agent hierarchy:

```
Goal: "Build an e-commerce scraper"
├── Agent 1: Design architecture
│   ├── Sub-Agent 1.1: Define data models
│   └── Sub-Agent 1.2: Plan scraping strategy
├── Agent 2: Implement core logic
│   ├── Sub-Agent 2.1: Write HTTP client
│   └── Sub-Agent 2.2: Create parsers
└── Agent 3: Add polish
    ├── Sub-Agent 3.1: Error handling
    └── Sub-Agent 3.2: Testing
```

**Execution Flow:**

1. **Task Reception**: Platform receives a goal with optional requirements
2. **Complexity Assessment**: Determines if task needs decomposition
3. **Decomposition** (if complex): Breaks into subtasks using LLM
4. **Agent Creation**: Spawns sub-agents for each subtask
5. **Recursive Execution**: Each sub-agent repeats steps 2-4
6. **Evaluation**: Results are validated against requirements
7. **Self-Correction**: Failed tasks retry automatically
8. **Aggregation**: Results bubble up through the hierarchy
9. **Cleanup**: Successful agents are deactivated

## ⚙️ Configuration

### Via Code

```python
platform = AgenticPlatform(
    api_key="your-key",
    model="gpt-4",
    provider="openai",
    base_url=None,  # Optional custom endpoint
    max_depth=3,         # Max recursion depth
    max_retries=5,       # Retry attempts per task
    timeout_per_task=300 # Timeout in seconds
)
```

### Via config.yaml

Edit `config.yaml` to customize:

```yaml
llm:
  provider: "openai"
  model: "gpt-4"
  temperature: 0.7
  max_tokens: 4096

agent:
  max_depth: 3
  max_retries: 5
  timeout_per_task: 300

decomposition:
  min_complexity_threshold: 100
  max_subtasks_per_level: 5

evaluation:
  enabled: true
  min_passing_score: 7

resources:
  max_concurrent_agents: 10
  token_budget_per_task: 8000
```

## 📚 API Reference

### Main Classes

#### `AgenticPlatform`

The main platform class that orchestrates agent execution.

**Parameters:**
- `api_key` (str): API key for LLM provider
- `model` (str): Model name (default: "gpt-4")
- `provider` (str): Provider type ("openai", "deepseek", "custom")
- `base_url` (str, optional): Custom API endpoint
- `max_depth` (int): Maximum recursion depth (default: 3)
- `max_retries` (int): Max retry attempts per task (default: 5)
- `use_mock` (bool): Use mock LLM for testing (default: False)

**Methods:**
- `execute_sync(goal, requirements)`: Synchronous execution
- `execute(goal, requirements)`: Async execution
- Both return dict with: `success`, `result`, `error`, `execution_time`, `attempts`, `total_subagents`

#### `solve()` Convenience Function

```python
from agentic_platform import solve

result = solve(
    goal="Your goal here",
    requirements=["req1", "req2"],
    api_key="your-key",
    provider="openai",
    model="gpt-4",
    max_depth=3,
    max_retries=5,
    use_mock=False
)
```

### Task & Agent Classes

#### `Task`
Represents a unit of work with status tracking.

**Attributes:**
- `id`: Unique identifier
- `description`: Task description
- `requirements`: List of requirements
- `status`: TaskStatus enum (PENDING, IN_PROGRESS, COMPLETED, FAILED, RETRYING)
- `result`: Execution result
- `error`: Error message if failed
- `attempts`: Number of attempts

#### `SubAgent`
Autonomous agent that executes tasks recursively.

## 🧪 Testing

### Run Tests

```bash
pytest tests.py -v
```

### Test with Mock LLM

```python
from agentic_platform import solve

# No API key needed - uses mock responses
result = solve("Create a function", use_mock=True)
```

### Example Scripts

```bash
# Run basic examples
python examples.py

# Run specific example
python -c "from examples import example_deepseek; example_deepseek()"
```

## 🔍 Troubleshooting

### Authentication Errors

**Error**: `Authentication Fails, Your api key is invalid`

**Solutions:**
- Verify API key is correct
- Check for extra spaces or quotes
- Ensure environment variable is set: `export OPENAI_API_KEY="sk-..."`

### Rate Limiting

**Error**: `Rate limit exceeded`

**Solutions:**
- Reduce concurrent agents in config
- Add delays between requests
- Upgrade your API plan

### Model Not Found

**Error**: `Model xyz not found`

**Solutions:**
- Verify model name spelling
- Check model availability in your region
- Confirm you have access to the model

### Server Won't Start (Web Interface)

```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process
kill -9 <PID>

# Or use different port
```

### Events Not Showing in Web Interface

- Check browser console (F12) for errors
- Ensure JavaScript is enabled
- Try Chrome or Firefox

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with support for multiple LLM providers
- Inspired by autonomous agent research
- Community contributions welcome

---

**Need Help?** Open an issue on GitHub or check the documentation above.

**Happy Agentic Computing! 🤖✨**