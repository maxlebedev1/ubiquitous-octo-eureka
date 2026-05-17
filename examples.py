"""
Example usage of the Recursive Agentic AI Platform.

This demonstrates how to use the platform to solve complex problems.
"""

from agentic_platform import AgenticPlatform, solve


def example_basic_usage():
    """Basic example with mock LLM."""
    print("=" * 60)
    print("BASIC USAGE EXAMPLE")
    print("=" * 60)
    
    # Simple goal with no requirements
    result = solve(
        goal="Write a function to calculate fibonacci numbers",
        use_mock=True,
        max_depth=2,
        max_retries=3
    )
    
    print(f"\nGoal: {result['goal']}")
    print(f"Success: {result['success']}")
    print(f"Execution time: {result['execution_time']:.2f}s")
    print(f"Max depth: {result['max_depth_reached']}")
    print(f"Sub-agents created: {result['total_subagents']}")
    

def example_with_requirements():
    """Example with specific requirements."""
    print("\n" + "=" * 60)
    print("EXAMPLE WITH REQUIREMENTS")
    print("=" * 60)
    
    goal = "Create a REST API for a todo application"
    requirements = [
        "Use FastAPI framework",
        "Include CRUD operations",
        "Add authentication with JWT",
        "Implement database models with SQLAlchemy",
        "Include input validation"
    ]
    
    result = solve(
        goal=goal,
        requirements=requirements,
        use_mock=True,
        max_depth=3,
        max_retries=5
    )
    
    print(f"\nGoal: {result['goal']}")
    print(f"Success: {result['success']}")
    print(f"Execution time: {result['execution_time']:.2f}s")
    print(f"Max depth: {result['max_depth_reached']}")
    print(f"Sub-agents created: {result['total_subagents']}")
    print(f"Attempts: {result['attempts']}")
    

def example_platform_class():
    """Example using the platform class directly."""
    print("\n" + "=" * 60)
    print("PLATFORM CLASS EXAMPLE")
    print("=" * 60)
    
    # Initialize platform
    platform = AgenticPlatform(
        api_key=None,  # Will use mock client
        model="gpt-4",
        max_depth=2,
        max_retries=3,
        use_mock=True
    )
    
    # Execute goal
    goal = "Build a data pipeline that processes CSV files and stores results in a database"
    requirements = [
        "Read from multiple CSV files",
        "Clean and validate data",
        "Transform data according to schema",
        "Store in PostgreSQL database",
        "Handle errors gracefully"
    ]
    
    result = platform.execute_sync(goal, requirements)
    
    print(f"\nGoal: {result['goal']}")
    print(f"Success: {result['success']}")
    print(f"Execution time: {result['execution_time']:.2f}s")
    print(f"Max depth: {result['max_depth_reached']}")
    print(f"Sub-agents created: {result['total_subagents']}")
    

def example_deepseek():
    """Example using DeepSeek API."""
    print("\n" + "=" * 60)
    print("DEEPSEEK EXAMPLE")
    print("=" * 60)
    
    import os
    
    # Get API key from environment variable
    api_key = os.getenv("DEEPSEEK_API_KEY", "your-deepseek-api-key")
    
    # Initialize platform with DeepSeek
    platform = AgenticPlatform(
        api_key=api_key,
        model="deepseek-chat",  # or "deepseek-coder" for coding tasks
        max_depth=2,
        max_retries=3,
        provider="deepseek"  # Specify DeepSeek as the provider
    )
    
    # Execute goal
    goal = "Write a Python function to sort a list using merge sort"
    requirements = [
        "Include type hints",
        "Add docstring with examples",
        "Include unit tests"
    ]
    
    result = platform.execute_sync(goal, requirements)
    
    print(f"\nGoal: {result['goal']}")
    print(f"Success: {result['success']}")
    print(f"Execution time: {result['execution_time']:.2f}s")
    print(f"Max depth: {result['max_depth_reached']}")
    print(f"Sub-agents created: {result['total_subagents']}")
    
    if result['result']:
        print("\nResult:")
        print(str(result['result'])[:500] + "...")


def example_custom_endpoint():
    """Example using a custom OpenAI-compatible endpoint (e.g., local LLM)."""
    print("\n" + "=" * 60)
    print("CUSTOM ENDPOINT EXAMPLE")
    print("=" * 60)
    
    import os
    
    # Example: Using Ollama locally
    platform = AgenticPlatform(
        api_key="ollama",  # Ollama doesn't require a real API key
        model="llama3",  # or your preferred model
        max_depth=2,
        max_retries=3,
        base_url="http://localhost:11434/v1",  # Ollama's OpenAI-compatible endpoint
        provider="custom"  # Use custom provider for any OpenAI-compatible API
    )
    
    # Execute goal
    goal = "Explain the concept of recursion in programming"
    
    result = platform.execute_sync(goal)
    
    print(f"\nGoal: {result['goal']}")
    print(f"Success: {result['success']}")
    print(f"Execution time: {result['execution_time']:.2f}s")
    
    if result['result']:
        print("\nResult:")
        print(str(result['result'])[:500] + "...")


def example_complex_goal():
    """Example with a complex, multi-step goal."""
    print("\n" + "=" * 60)
    print("COMPLEX GOAL EXAMPLE")
    print("=" * 60)
    
    goal = """
    Build a complete machine learning pipeline for sentiment analysis that includes:
    1. Data collection from social media APIs
    2. Data preprocessing and cleaning
    3. Feature extraction using TF-IDF
    4. Model training with multiple algorithms
    5. Model evaluation and comparison
    6. Deployment as a web service
    """
    
    requirements = [
        "Use Python with scikit-learn",
        "Include error handling",
        "Add logging throughout",
        "Create configuration files",
        "Write unit tests",
        "Document the code"
    ]
    
    result = solve(
        goal=goal,
        requirements=requirements,
        use_mock=True,
        max_depth=3,
        max_retries=5
    )
    
    print(f"\nGoal: Sentiment Analysis ML Pipeline")
    print(f"Success: {result['success']}")
    print(f"Execution time: {result['execution_time']:.2f}s")
    print(f"Max depth reached: {result['max_depth_reached']}")
    print(f"Total sub-agents created: {result['total_subagents']}")
    print(f"Attempts made: {result['attempts']}")
    
    if result['result']:
        print("\nResult preview:")
        print(str(result['result'])[:500] + "...")


if __name__ == "__main__":
    # Run all examples
    example_basic_usage()
    example_with_requirements()
    example_platform_class()
    example_complex_goal()
    
    # Uncomment to run DeepSeek example (requires API key)
    # example_deepseek()
    
    # Uncomment to run custom endpoint example (requires local server)
    # example_custom_endpoint()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
