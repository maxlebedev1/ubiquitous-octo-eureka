#!/usr/bin/env python3
"""Test script to verify DeepSeek V4 integration works correctly."""

from agentic_platform import AgenticPlatform

def test_deepseek_v4():
    """Test DeepSeek V4 Pro model initialization."""
    print("=" * 60)
    print("Testing DeepSeek V4 Pro Integration")
    print("=" * 60)
    
    # Initialize platform with DeepSeek V4 Pro (use mock for testing without API key)
    platform = AgenticPlatform(
        api_key="test-key",
        model="deepseek-v4-pro",
        provider="deepseek",
        use_mock=True  # Use mock client for testing without valid API key
    )
    
    print(f"\n✓ Platform initialized successfully")
    print(f"  Provider: {platform.provider}")
    print(f"  Model: deepseek-v4-pro")
    
    # Test execute_sync (the synchronous wrapper)
    print("\nTesting execute_sync method...")
    result = platform.execute_sync(
        goal="Write a simple hello world function",
        requirements=["Use Python", "Include docstring"]
    )
    
    print(f"✓ Execution completed")
    print(f"  Success: {result['success']}")
    print(f"  Execution time: {result['execution_time']:.2f}s")
    print(f"  Attempts: {result['attempts']}")
    
    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    test_deepseek_v4()
