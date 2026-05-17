# DeepSeek V4 Integration Guide

## Quick Start

The platform now fully supports **DeepSeek V4** and other DeepSeek models. Here's how to use it:

### Basic Usage with DeepSeek V4 Pro

```python
from agentic_platform import AgenticPlatform

# Initialize with DeepSeek V4 Pro
platform = AgenticPlatform(
    api_key="your-deepseek-api-key",  # Get from https://platform.deepseek.com/
    model="deepseek-v4-pro",           # DeepSeek V4 Pro model
    provider="deepseek",               # Specify DeepSeek provider
    max_depth=3,                       # Max recursion depth
    max_retries=5                      # Max retry attempts per task
)

# Execute a complex goal
result = platform.execute_sync(
    goal="Build a complete REST API for a todo application",
    requirements=[
        "Use FastAPI framework",
        "Include JWT authentication",
        "Add database models with SQLAlchemy",
        "Implement CRUD operations",
        "Include input validation"
    ]
)

print(f"Success: {result['success']}")
print(f"Result: {result['result']}")
```

### Using Environment Variables

```bash
# Set your DeepSeek API key
export DEEPSEEK_API_KEY="sk-your-actual-api-key"
```

```python
import os
from agentic_platform import AgenticPlatform

platform = AgenticPlatform(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    model="deepseek-v4-pro",
    provider="deepseek"
)

result = platform.execute_sync("Write a merge sort implementation in Python")
```

## Available DeepSeek Models

The platform supports all DeepSeek models:

| Model | Description | Best For |
|-------|-------------|----------|
| `deepseek-v4-pro` | Latest V4 Pro model | Complex reasoning, coding |
| `deepseek-chat` | General chat model | General tasks, conversation |
| `deepseek-coder` | Specialized coding model | Code generation, debugging |
| `deepseek-v3` | Previous generation | Cost-effective tasks |

## Async Usage

For async workflows:

```python
import asyncio
from agentic_platform import AgenticPlatform

async def main():
    platform = AgenticPlatform(
        api_key="your-api-key",
        model="deepseek-v4-pro",
        provider="deepseek"
    )
    
    result = await platform.execute(
        goal="Create a data pipeline for processing CSV files",
        requirements=["Handle errors gracefully", "Log all operations"]
    )
    
    return result

# Run the async function
result = asyncio.run(main())
```

## Custom Base URL (Advanced)

If you need to use a custom DeepSeek endpoint:

```python
platform = AgenticPlatform(
    api_key="your-api-key",
    model="deepseek-v4-pro",
    provider="deepseek",
    base_url="https://custom-deepseek-endpoint.com/v1"
)
```

## Complete Example with Error Handling

```python
from agentic_platform import AgenticPlatform
import os

def solve_with_deepseek(goal: str, requirements: list = None):
    """Solve a complex problem using DeepSeek V4."""
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY environment variable not set")
    
    platform = AgenticPlatform(
        api_key=api_key,
        model="deepseek-v4-pro",
        provider="deepseek",
        max_depth=3,
        max_retries=5
    )
    
    try:
        result = platform.execute_sync(goal, requirements)
        
        if result['success']:
            print(f"✓ Task completed in {result['execution_time']:.2f}s")
            print(f"  Attempts: {result['attempts']}")
            print(f"  Sub-agents created: {result['total_subagents']}")
            return result['result']
        else:
            print(f"✗ Task failed: {result['error']}")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

# Usage
if __name__ == "__main__":
    goal = """
    Create a machine learning pipeline for sentiment analysis that includes:
    1. Data collection from Twitter API
    2. Text preprocessing and cleaning
    3. Feature extraction with TF-IDF
    4. Model training with multiple algorithms
    5. Evaluation and comparison
    6. Deployment as a Flask web service
    """
    
    requirements = [
        "Use Python with scikit-learn",
        "Include comprehensive error handling",
        "Add logging throughout",
        "Write unit tests",
        "Document all functions"
    ]
    
    result = solve_with_deepseek(goal, requirements)
```

## Migration from OpenAI

If you're migrating from OpenAI, the change is minimal:

### Before (OpenAI):
```python
platform = AgenticPlatform(
    api_key="sk-openai-key",
    model="gpt-4",
    provider="openai"
)
```

### After (DeepSeek):
```python
platform = AgenticPlatform(
    api_key="sk-deepseek-key",
    model="deepseek-v4-pro",
    provider="deepseek"
)
```

## Testing Without API Key

For testing purposes, you can use the mock client:

```python
platform = AgenticPlatform(
    api_key="test-key",
    model="deepseek-v4-pro",
    provider="deepseek",
    use_mock=True  # Uses mock responses
)

result = platform.execute_sync("Test goal")
```

## Performance Tips

1. **Adjust `max_depth`**: 
   - Simple tasks: `max_depth=1-2`
   - Complex tasks: `max_depth=3-5`
   
2. **Tune `max_retries`**:
   - Stable models: `max_retries=3`
   - Complex tasks: `max_retries=5`

3. **Choose the right model**:
   - Coding tasks: `deepseek-coder` or `deepseek-v4-pro`
   - General tasks: `deepseek-chat`
   - Cost-sensitive: `deepseek-v3`

## Troubleshooting

### Authentication Errors
```
Error: Authentication Fails, Your api key is invalid
```
**Solution**: Verify your API key is correct and has sufficient credits.

### Rate Limiting
```
Error: Rate limit exceeded
```
**Solution**: Reduce concurrent requests or upgrade your plan.

### Model Not Found
```
Error: Model deepseek-v4-pro not found
```
**Solution**: Check the model name is correct and available in your region.

## Getting a DeepSeek API Key

1. Visit [DeepSeek Platform](https://platform.deepseek.com/)
2. Create an account
3. Navigate to API Keys section
4. Generate a new API key
5. Copy and store securely

---

**Note**: The platform automatically handles recursive task decomposition, evaluation, and retries. You only need to specify your goal and requirements!
