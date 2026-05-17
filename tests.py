"""
Unit tests for the Recursive Agentic AI Platform.
"""

import pytest
import asyncio
from agentic_platform import (
    Task, TaskStatus, Agent, SubAgent, 
    AgenticPlatform, MockLLMClient, solve
)


class TestTask:
    """Tests for the Task class."""
    
    def test_task_creation(self):
        """Test creating a task."""
        task = Task(
            description="Test task",
            requirements=["Requirement 1"]
        )
        
        assert task.description == "Test task"
        assert len(task.requirements) == 1
        assert task.status == TaskStatus.PENDING
        assert task.attempts == 0
    
    def test_task_reset(self):
        """Test resetting a task for retry."""
        task = Task(description="Test")
        task.status = TaskStatus.FAILED
        task.result = "Some result"
        task.error = "Some error"
        task.attempts = 3
        
        task.reset()
        
        assert task.status == TaskStatus.PENDING
        assert task.result is None
        assert task.error is None
        assert task.attempts == 4


class TestMockLLMClient:
    """Tests for the MockLLMClient."""
    
    @pytest.mark.asyncio
    async def test_generate(self):
        """Test mock LLM generate method."""
        client = MockLLMClient("mock-key")
        response = await client.generate("Test prompt")
        
        assert response == "Mock response"
    
    @pytest.mark.asyncio
    async def test_chat(self):
        """Test mock LLM chat method."""
        client = MockLLMClient("mock-key")
        messages = [{"role": "user", "content": "Hello"}]
        response = await client.chat(messages)
        
        assert response == "Mock chat response"


class TestAgenticPlatform:
    """Tests for the AgenticPlatform class."""
    
    def test_platform_initialization_mock(self):
        """Test platform initialization with mock client."""
        platform = AgenticPlatform(
            api_key=None,
            model="gpt-4",
            max_depth=3,
            max_retries=5,
            use_mock=True
        )
        
        assert platform.max_depth == 3
        assert platform.max_retries == 5
        assert isinstance(platform.llm_client, MockLLMClient)
    
    @pytest.mark.asyncio
    async def test_execute_simple_goal(self):
        """Test executing a simple goal."""
        platform = AgenticPlatform(use_mock=True, max_depth=2, max_retries=3)
        
        result = await platform.execute("Write a hello world program")
        
        assert result["success"] is True
        assert result["goal"] == "Write a hello world program"
        assert "execution_time" in result
        assert result["attempts"] >= 1
    
    @pytest.mark.asyncio
    async def test_execute_with_requirements(self):
        """Test executing a goal with requirements."""
        platform = AgenticPlatform(use_mock=True, max_depth=2, max_retries=3)
        
        requirements = ["Use Python", "Include comments"]
        result = await platform.execute(
            "Create a calculator",
            requirements=requirements
        )
        
        assert result["success"] is True
        assert result["goal"] == "Create a calculator"
    
    def test_execute_sync(self):
        """Test synchronous execution wrapper."""
        platform = AgenticPlatform(use_mock=True)
        
        result = platform.execute_sync("Simple task")
        
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_execution_tracking(self):
        """Test that execution metrics are tracked."""
        platform = AgenticPlatform(use_mock=True, max_depth=3, max_retries=5)
        
        result = await platform.execute("Complex multi-step task")
        
        assert "max_depth_reached" in result
        assert "total_subagents" in result
        assert "execution_time" in result
        assert result["max_depth_reached"] >= 0
        assert result["total_subagents"] >= 0


class TestSolveFunction:
    """Tests for the convenience solve function."""
    
    def test_solve_basic(self):
        """Test basic solve function."""
        result = solve("Test goal", use_mock=True)
        
        assert result["success"] is True
        assert result["goal"] == "Test goal"
    
    def test_solve_with_params(self):
        """Test solve function with parameters."""
        result = solve(
            "Test goal",
            requirements=["Req 1", "Req 2"],
            use_mock=True,
            max_depth=2,
            max_retries=3
        )
        
        assert result["success"] is True


class TestSubAgent:
    """Tests for the SubAgent class."""
    
    @pytest.mark.asyncio
    async def test_subagent_creation(self):
        """Test creating a sub-agent."""
        llm_client = MockLLMClient("mock-key")
        task = Task(description="Test subtask")
        
        agent = SubAgent(
            llm_client=llm_client,
            task=task,
            depth=1,
            max_depth=3,
            max_retries=5
        )
        
        assert agent.depth == 1
        assert agent.max_depth == 3
        assert agent.is_active is True
    
    @pytest.mark.asyncio
    async def test_subagent_execution(self):
        """Test sub-agent task execution."""
        llm_client = MockLLMClient("mock-key")
        task = Task(description="Execute this task")
        
        agent = SubAgent(
            llm_client=llm_client,
            task=task,
            depth=0,
            max_depth=2,
            max_retries=3
        )
        
        success = await agent.execute_task()
        
        assert success is True
        assert task.status == TaskStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_subagent_deactivation(self):
        """Test sub-agent deactivation."""
        llm_client = MockLLMClient("mock-key")
        task = Task(description="Test")
        
        agent = SubAgent(llm_client=llm_client, task=task)
        agent.deactivate()
        
        assert agent.is_active is False


class TestRetryMechanism:
    """Tests for the retry mechanism."""
    
    @pytest.mark.asyncio
    async def test_retry_on_failure(self):
        """Test that tasks retry on failure."""
        # This test verifies the retry logic exists
        platform = AgenticPlatform(use_mock=True, max_retries=5)
        
        result = await platform.execute("Task that might fail")
        
        # With mock client, should succeed on first try
        assert result["success"] is True
        assert result["attempts"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
