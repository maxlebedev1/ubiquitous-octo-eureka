#!/usr/bin/env python3
"""
Demonstration of DeepSeek V4 Pro usage with the agentic platform.

This shows the correct way to use the platform with DeepSeek V4 Pro,
avoiding the coroutine warning you encountered.
"""

from agentic_platform import AgenticPlatform
import os

def demo_deepseek_v4_pro():
    """Demonstrate using DeepSeek V4 Pro with the platform."""
    
    print("=" * 70)
    print("DeepSeek V4 Pro Integration Demo")
    print("=" * 70)
    
    # Get API key from environment or use placeholder
    api_key = os.getenv("DEEPSEEK_API_KEY", "your-deepseek-api-key-here")
    
    # Initialize the platform with DeepSeek V4 Pro
    print("\n1. Initializing platform with DeepSeek V4 Pro...")
    platform = AgenticPlatform(
        api_key=api_key,
        model="deepseek-v4-pro",  # DeepSeek V4 Pro model
        provider="deepseek",       # Specify DeepSeek as provider
        max_depth=2,               # Break down tasks up to 2 levels deep
        max_retries=5              # Retry failed tasks up to 5 times
    )
    print("   ✓ Platform initialized successfully")
    
    # Define a complex goal
    goal = "Write a Python function to implement binary search"
    requirements = [
        "Include type hints",
        "Add comprehensive docstring",
        "Handle edge cases",
        "Include unit tests"
    ]
    
    print(f"\n2. Executing goal: {goal}")
    print(f"   Requirements: {len(requirements)} specified")
    
    # IMPORTANT: Use execute_sync() for synchronous execution
    # This is what you were missing - execute() is async and needs await
    print("\n3. Running task (using execute_sync for synchronous execution)...")
    result = platform.execute_sync(goal, requirements)
    
    # Display results
    print("\n4. Results:")
    print(f"   Success: {result['success']}")
    print(f"   Execution time: {result['execution_time']:.2f} seconds")
    print(f"   Attempts made: {result['attempts']}")
    print(f"   Sub-agents created: {result['total_subagents']}")
    print(f"   Max depth reached: {result['max_depth_reached']}")
    
    if result['result']:
        print("\n5. Generated Result (first 500 chars):")
        print("-" * 70)
        print(str(result['result'])[:500])
        if len(str(result['result'])) > 500:
            print("...")
        print("-" * 70)
    
    if result['error']:
        print(f"\n6. Error (if any): {result['error']}")
    
    print("\n" + "=" * 70)
    print("Demo completed!")
    print("=" * 70)
    
    return result


def demo_with_mock():
    """Demonstrate using mock client for testing without API key."""
    
    print("\n" + "=" * 70)
    print("Mock Client Demo (No API Key Required)")
    print("=" * 70)
    
    # Initialize with mock client
    platform = AgenticPlatform(
        api_key="test-key",
        model="deepseek-v4-pro",
        provider="deepseek",
        use_mock=True  # Use mock responses for testing
    )
    
    result = platform.execute_sync(
        goal="Explain recursion in programming",
        requirements=["Use simple examples", "Keep it under 200 words"]
    )
    
    print(f"\nSuccess: {result['success']}")
    print(f"Execution time: {result['execution_time']:.2f}s")
    print("✓ Mock client works correctly!")
    
    return result


if __name__ == "__main__":
    # Run the demo with mock client (works without API key)
    demo_with_mock()
    
    # To run with real DeepSeek API:
    # 1. Set your API key: export DEEPSEEK_API_KEY="your-key-here"
    # 2. Uncomment the line below:
    # demo_deepseek_v4_pro()
    
    print("\n" + "=" * 70)
    print("IMPORTANT NOTES:")
    print("=" * 70)
    print("""
1. The error you saw was because execute() is an async method.
   Solution: Use execute_sync() for synchronous execution, or
             use asyncio.run() / await in an async function.

2. For production use with DeepSeek V4 Pro:
   - Get API key from https://platform.deepseek.com/
   - Set environment variable: export DEEPSEEK_API_KEY="your-key"
   - Use model="deepseek-v4-pro" and provider="deepseek"

3. The platform will:
   - Break down complex goals into subtasks
   - Create sub-agents recursively (up to max_depth)
   - Evaluate each task's outcome
   - Retry failed tasks (up to max_retries)
   - Clean up sub-agents after completion
    """)
    print("=" * 70)
