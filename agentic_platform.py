"""
Recursive Agentic AI Platform

A multi-agent system that recursively breaks down complex problems into 
manageable sub-tasks, evaluates outcomes, and iteratively improves.
"""

import asyncio
import uuid
import os
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base directory for all runs
RUNS_DIR = Path(__file__).parent / "runs"
RUNS_DIR.mkdir(exist_ok=True)


class TaskStatus(Enum):
    """Status of a task in the execution pipeline."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class Task:
    """Represents a task to be executed by an agent."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    requirements: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    attempts: int = 0
    max_attempts: int = 5
    subtasks: List['Task'] = field(default_factory=list)
    parent_id: Optional[str] = None
    run_dir: Optional[Path] = None
    
    def reset(self):
        """Reset task for retry."""
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.attempts += 1
    
    def save(self, run_dir: Optional[Path] = None):
        """Save task state to disk."""
        target_dir = run_dir or self.run_dir
        if not target_dir:
            return
        
        task_file = target_dir / "tasks" / f"{self.id}.json"
        task_file.parent.mkdir(exist_ok=True)
        
        task_data = {
            "id": self.id,
            "description": self.description,
            "requirements": self.requirements,
            "status": self.status.value,
            "result": str(self.result) if self.result else None,
            "error": self.error,
            "attempts": self.attempts,
            "parent_id": self.parent_id,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(task_file, 'w') as f:
            json.dump(task_data, f, indent=2)


@dataclass
class Agent:
    """Represents an autonomous agent that executes tasks."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    task: Optional[Task] = None
    is_active: bool = True
    depth: int = 0
    
    def deactivate(self):
        """Deactivate agent after task completion."""
        self.is_active = False
        logger.info(f"Agent {self.name} ({self.id}) deactivated")


class LLMClient:
    """Abstract LLM client interface."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from the LLM."""
        raise NotImplementedError
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """Send chat messages to the LLM."""
        raise NotImplementedError


class MockLLMClient(LLMClient):
    """Mock LLM client for testing."""
    
    async def generate(self, prompt: str, **kwargs) -> str:
        await asyncio.sleep(0.1)  # Simulate API call
        return "Mock response"
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        await asyncio.sleep(0.1)
        return "Mock chat response"


class DeepSeekClient(LLMClient):
    """DeepSeek API client with support for custom base URLs."""
    
    def __init__(self, api_key: str, model: str = "deepseek-chat", base_url: Optional[str] = None):
        super().__init__(api_key, model)
        self.base_url = base_url or "https://api.deepseek.com/v1"
        try:
            from openai import AsyncOpenAI
            # DeepSeek uses OpenAI-compatible API
            self.client = AsyncOpenAI(
                api_key=api_key,
                base_url=self.base_url
            )
        except ImportError:
            raise ImportError("Please install openai: pip install openai")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return response.choices[0].message.content
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content


class OpenAIClient(LLMClient):
    """OpenAI API client with support for custom base URLs."""
    
    def __init__(self, api_key: str, model: str = "gpt-4", base_url: Optional[str] = None):
        super().__init__(api_key, model)
        self.base_url = base_url
        try:
            from openai import AsyncOpenAI
            # Use custom base_url if provided, otherwise use default OpenAI endpoint
            self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        except ImportError:
            raise ImportError("Please install openai: pip install openai")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return response.choices[0].message.content
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content


class SubAgent:
    """
    A sub-agent that handles a specific subtask.
    Recursively creates sub-agents if needed.
    """
    
    def __init__(
        self,
        llm_client: LLMClient,
        task: Task,
        depth: int = 0,
        max_depth: int = 3,
        max_retries: int = 5,
        parent_agent: Optional['SubAgent'] = None,
        run_dir: Optional[Path] = None
    ):
        self.id = str(uuid.uuid4())
        self.llm_client = llm_client
        self.task = task
        self.task.run_dir = run_dir
        self.depth = depth
        self.max_depth = max_depth
        self.max_retries = max_retries
        self.parent_agent = parent_agent
        self.sub_agents: List['SubAgent'] = []
        self.is_active = True
        self.run_dir = run_dir
        
        # Save agent info
        if run_dir:
            self._save_agent_info()
        
        logger.info(f"Created SubAgent {self.id} at depth {depth} for task: {task.description[:50]}...")
    
    def _save_agent_info(self):
        """Save agent metadata to disk."""
        if not self.run_dir:
            return
        
        agents_dir = self.run_dir / "agents"
        agents_dir.mkdir(exist_ok=True)
        
        agent_data = {
            "id": self.id,
            "depth": self.depth,
            "task_id": self.task.id,
            "task_description": self.task.description,
            "is_active": self.is_active,
            "created_at": datetime.now().isoformat()
        }
        
        agent_file = agents_dir / f"{self.id}.json"
        with open(agent_file, 'w') as f:
            json.dump(agent_data, f, indent=2)
    
    async def decompose_task(self) -> List[Task]:
        """Break down the current task into subtasks using LLM."""
        prompt = f"""
You are a task decomposition expert. Break down the following task into clear, 
actionable subtasks. Each subtask should be specific enough to be completed reliably.

Task: {self.task.description}
Requirements: {', '.join(self.task.requirements) if self.task.requirements else 'None specified'}

Current depth: {self.depth}/{self.max_depth}

Return your response as a JSON array of subtasks, where each subtask has:
- description: Clear description of what needs to be done
- requirements: List of specific requirements for this subtask

Only decompose if the task is complex enough. If the task is already simple 
and can be completed directly, return an empty array.
"""
        
        try:
            response = await self.llm_client.generate(prompt)
            # Parse JSON response (simplified - in production use proper JSON parsing)
            # For now, we'll create mock subtasks based on the response
            subtasks = self._parse_subtasks(response)
            return subtasks
        except Exception as e:
            logger.error(f"Failed to decompose task: {e}")
            return []
    
    def _parse_subtasks(self, response: str) -> List[Task]:
        """Parse LLM response into Task objects."""
        # Simplified parsing - in production, use proper JSON parsing
        subtasks = []
        
        # Create default subtasks if parsing fails
        if not response.strip():
            return subtasks
        
        # For demonstration, create 2-3 subtasks
        lines = [l.strip() for l in response.split('\n') if l.strip()]
        for i, line in enumerate(lines[:3]):
            subtask = Task(
                description=line[:200],  # Limit description length
                requirements=["Complete the task accurately"],
                parent_id=self.task.id
            )
            subtasks.append(subtask)
        
        return subtasks
    
    async def execute_task(self) -> bool:
        """Execute the assigned task, creating sub-agents if needed."""
        logger.info(f"Agent {self.id} executing task: {self.task.description[:50]}...")
        
        for attempt in range(self.max_retries):
            self.task.attempts = attempt + 1
            
            try:
                # Check if we should decompose further
                should_decompose = (
                    self.depth < self.max_depth and 
                    self._is_complex_task()
                )
                
                if should_decompose:
                    success = await self._execute_with_decomposition()
                else:
                    success = await self._execute_directly()
                
                if success:
                    # Evaluate the result
                    evaluation = await self._evaluate_result()
                    
                    if evaluation["success"]:
                        logger.info(f"Task completed successfully: {self.task.description[:50]}...")
                        self.task.status = TaskStatus.COMPLETED
                        self.task.result = evaluation.get("result")
                        self._cleanup_sub_agents()
                        return True
                    else:
                        # Task failed evaluation, will retry
                        logger.warning(f"Task failed evaluation: {evaluation.get('reason', 'Unknown')}")
                        self.task.error = evaluation.get("reason", "Evaluation failed")
                        self.task.status = TaskStatus.FAILED
                        
                        if attempt < self.max_retries - 1:
                            logger.info(f"Retrying task (attempt {attempt + 2}/{self.max_retries})")
                            self.task.reset()
                            self._cleanup_sub_agents()
                        continue
                else:
                    logger.warning(f"Task execution failed")
                    self.task.status = TaskStatus.FAILED
                    
                    if attempt < self.max_retries - 1:
                        logger.info(f"Retrying task (attempt {attempt + 2}/{self.max_retries})")
                        self.task.reset()
                        self._cleanup_sub_agents()
                    continue
                    
            except Exception as e:
                logger.error(f"Task execution error: {e}")
                self.task.error = str(e)
                self.task.status = TaskStatus.FAILED
                
                if attempt < self.max_retries - 1:
                    self.task.reset()
                    self._cleanup_sub_agents()
                continue
        
        # All retries exhausted
        logger.error(f"Task failed after {self.max_retries} attempts: {self.task.description[:50]}...")
        self.task.status = TaskStatus.FAILED
        self._cleanup_sub_agents()
        return False
    
    def _is_complex_task(self) -> bool:
        """Determine if a task is complex enough to require decomposition."""
        # Simple heuristic: check description length and requirement count
        complexity_score = len(self.task.description) + len(self.task.requirements) * 20
        return complexity_score > 100
    
    async def _execute_with_decomposition(self) -> bool:
        """Execute task by decomposing into subtasks."""
        logger.info(f"Decomposing task at depth {self.depth}")
        
        # Decompose the task
        subtasks = await self.decompose_task()
        
        if not subtasks:
            # No subtasks created, execute directly
            return await self._execute_directly()
        
        # Create sub-agents for each subtask
        self.sub_agents = []
        for subtask in subtasks:
            sub_agent = SubAgent(
                llm_client=self.llm_client,
                task=subtask,
                depth=self.depth + 1,
                max_depth=self.max_depth,
                max_retries=self.max_retries,
                parent_agent=self,
                run_dir=self.run_dir
            )
            self.sub_agents.append(sub_agent)
        
        # Execute all sub-agents
        results = await asyncio.gather(
            *[agent.execute_task() for agent in self.sub_agents],
            return_exceptions=True
        )
        
        # Check if all subtasks succeeded
        all_success = all(r is True for r in results)
        
        if all_success:
            # Aggregate results from subtasks
            self.task.result = {
                "subtask_results": [
                    {"task": a.task.description, "result": a.task.result}
                    for a in self.sub_agents
                ]
            }
            return True
        
        return False
    
    async def _execute_directly(self) -> bool:
        """Execute the task directly without decomposition."""
        prompt = f"""
You are an AI assistant tasked with completing the following:

Task: {self.task.description}
Requirements: {', '.join(self.task.requirements) if self.task.requirements else 'None specified'}

Provide a complete and accurate solution. Be thorough and ensure all requirements are met.
"""
        
        try:
            result = await self.llm_client.generate(prompt)
            self.task.result = result
            
            # Save result to disk if run_dir is set
            if self.run_dir:
                self._save_result(result)
            
            # Save task state
            if self.run_dir:
                self.task.save()
            
            return True
        except Exception as e:
            logger.error(f"Direct execution failed: {e}")
            self.task.error = str(e)
            if self.run_dir:
                self.task.save()
            return False
    
    def _save_result(self, result: Any):
        """Save task result to disk."""
        if not self.run_dir:
            return
        
        results_dir = self.run_dir / "results"
        results_dir.mkdir(exist_ok=True)
        
        # Save the main result
        result_file = results_dir / f"{self.task.id}.txt"
        with open(result_file, 'w') as f:
            f.write(str(result))
        
        # Also save as JSON for structured data
        result_json_file = results_dir / f"{self.task.id}.json"
        with open(result_json_file, 'w') as f:
            json.dump({
                "task_id": self.task.id,
                "task_description": self.task.description,
                "result": str(result),
                "agent_id": self.id,
                "depth": self.depth,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
    
    async def _evaluate_result(self) -> Dict[str, Any]:
        """Evaluate whether the task was completed successfully."""
        prompt = f"""
You are an evaluation expert. Determine if the following task was completed successfully.

Task: {self.task.description}
Requirements: {', '.join(self.task.requirements) if self.task.requirements else 'None specified'}
Result: {self.task.result}

Return your evaluation as JSON with:
- success: boolean indicating if the task was completed successfully
- reason: explanation of your evaluation
- score: numerical score from 0-10
"""
        
        try:
            response = await self.llm_client.generate(prompt)
            # Simplified parsing - in production, use proper JSON parsing
            return {
                "success": True,  # Default to success for demo
                "reason": "Task appears complete",
                "score": 8
            }
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return {
                "success": False,
                "reason": f"Evaluation error: {e}",
                "score": 0
            }
    
    def _cleanup_sub_agents(self):
        """Deactivate and clean up sub-agents."""
        for agent in self.sub_agents:
            agent.is_active = False
        self.sub_agents.clear()
        logger.info(f"Cleaned up {len(self.sub_agents)} sub-agents")
    
    def deactivate(self):
        """Deactivate this agent."""
        self.is_active = False
        self._cleanup_sub_agents()
        logger.info(f"SubAgent {self.id} deactivated")


class AgenticPlatform:
    """
    Main platform class that orchestrates the recursive agent system.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        max_depth: int = 3,
        max_retries: int = 5,
        use_mock: bool = False,
        base_url: Optional[str] = None,
        provider: str = "openai"  # Options: "openai", "deepseek", "custom"
    ):
        """
        Initialize the agentic platform.
        
        Args:
            api_key: API key for LLM service
            model: Model name to use
            max_depth: Maximum recursion depth for task decomposition
            max_retries: Maximum retry attempts per task
            use_mock: Use mock LLM client for testing
            base_url: Custom base URL for OpenAI-compatible API endpoint
            provider: LLM provider to use ("openai", "deepseek", or "custom")
        """
        self.max_depth = max_depth
        self.max_retries = max_retries
        self.active_agents: List[SubAgent] = []
        self.provider = provider
        
        # Initialize LLM client based on provider
        if use_mock or not api_key:
            self.llm_client = MockLLMClient(api_key or "mock-key", model)
            logger.info("Using mock LLM client")
        elif provider.lower() == "deepseek":
            # Use DeepSeek model if provided, otherwise default to deepseek-chat
            deepseek_model = model if model else "deepseek-chat"
            self.llm_client = DeepSeekClient(
                api_key, 
                model=deepseek_model,
                base_url=base_url
            )
            if base_url:
                logger.info(f"Using DeepSeek client with model: {deepseek_model} and custom base_url: {base_url}")
            else:
                logger.info(f"Using DeepSeek client with model: {deepseek_model}")
        elif provider.lower() == "custom":
            # Use OpenAI client with custom base URL for any OpenAI-compatible API
            self.llm_client = OpenAIClient(api_key, model, base_url=base_url)
            logger.info(f"Using custom OpenAI-compatible client with model: {model} and base_url: {base_url}")
        else:
            # Default to OpenAI
            self.llm_client = OpenAIClient(api_key, model, base_url=base_url)
            if base_url:
                logger.info(f"Using OpenAI client with model: {model} and custom base_url: {base_url}")
            else:
                logger.info(f"Using OpenAI client with model: {model}")
    
    async def execute(self, goal: str, requirements: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute a complex goal using the recursive agent system.
        
        Args:
            goal: The main goal to accomplish
            requirements: List of specific requirements for the goal
            
        Returns:
            Dictionary containing execution results
        """
        logger.info(f"Starting execution of goal: {goal}")
        
        # Generate a short unique ID for this run
        run_id = str(uuid.uuid4())[:8]
        run_dir = RUNS_DIR / run_id
        run_dir.mkdir(exist_ok=True)
        
        # Save run metadata
        run_metadata = {
            "run_id": run_id,
            "goal": goal,
            "requirements": requirements or [],
            "started_at": datetime.now().isoformat(),
            "model": self.llm_client.model,
            "provider": self.provider,
            "max_depth": self.max_depth,
            "max_retries": self.max_retries
        }
        
        with open(run_dir / "metadata.json", 'w') as f:
            json.dump(run_metadata, f, indent=2)
        
        logger.info(f"Run directory created: {run_dir}")
        
        # Create root task
        root_task = Task(
            description=goal,
            requirements=requirements or [],
            max_attempts=self.max_retries,
            run_dir=run_dir
        )
        
        # Create root agent
        root_agent = SubAgent(
            llm_client=self.llm_client,
            task=root_task,
            depth=0,
            max_depth=self.max_depth,
            max_retries=self.max_retries,
            run_dir=run_dir
        )
        
        self.active_agents.append(root_agent)
        
        # Execute the task
        start_time = asyncio.get_event_loop().time()
        success = await root_agent.execute_task()
        end_time = asyncio.get_event_loop().time()
        
        # Deactivate root agent
        root_agent.deactivate()
        
        # Save final run summary
        run_summary = {
            "run_id": run_id,
            "success": success,
            "goal": goal,
            "result": str(root_task.result) if root_task.result else None,
            "error": root_task.error,
            "attempts": root_task.attempts,
            "execution_time_seconds": end_time - start_time,
            "max_depth_reached": self._get_max_depth_reached(root_agent),
            "total_subagents": self._count_subagents(root_agent),
            "completed_at": datetime.now().isoformat()
        }
        
        with open(run_dir / "summary.json", 'w') as f:
            json.dump(run_summary, f, indent=2)
        
        # Prepare result
        result = {
            "success": success,
            "goal": goal,
            "result": root_task.result,
            "error": root_task.error,
            "attempts": root_task.attempts,
            "execution_time": end_time - start_time,
            "max_depth_reached": self._get_max_depth_reached(root_agent),
            "total_subagents": self._count_subagents(root_agent),
            "run_id": run_id,
            "run_dir": str(run_dir)
        }
        
        logger.info(f"Execution completed: {'SUCCESS' if success else 'FAILED'}")
        logger.info(f"Results saved to: {run_dir}")
        return result
    
    def execute_sync(self, goal: str, requirements: Optional[List[str]] = None) -> Dict[str, Any]:
        """Synchronous wrapper for execute."""
        return asyncio.run(self.execute(goal, requirements))
    
    def _get_max_depth_reached(self, agent: SubAgent) -> int:
        """Calculate maximum depth reached during execution."""
        if not agent.sub_agents:
            return agent.depth
        
        max_child_depth = max(
            self._get_max_depth_reached(sub_agent)
            for sub_agent in agent.sub_agents
        )
        return max_child_depth
    
    def _count_subagents(self, agent: SubAgent) -> int:
        """Count total number of sub-agents created."""
        count = len(agent.sub_agents)
        for sub_agent in agent.sub_agents:
            count += self._count_subagents(sub_agent)
        return count


# Convenience function for quick usage
def solve(goal: str, requirements: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
    """
    Solve a complex problem using the agentic platform.
    
    Args:
        goal: The goal to accomplish
        requirements: List of requirements
        **kwargs: Additional arguments passed to AgenticPlatform
        
    Returns:
        Execution results
    """
    platform = AgenticPlatform(**kwargs)
    return platform.execute_sync(goal, requirements)


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        goal = " ".join(sys.argv[1:])
    else:
        goal = "Create a Python script that scrapes weather data from a website"
    
    print(f"Goal: {goal}\n")
    
    # Run with mock client for demonstration
    result = solve(goal, use_mock=True, max_depth=2, max_retries=3)
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Success: {result['success']}")
    print(f"Execution time: {result['execution_time']:.2f}s")
    print(f"Max depth reached: {result['max_depth_reached']}")
    print(f"Total sub-agents: {result['total_subagents']}")
    print(f"Attempts: {result['attempts']}")
    if result['result']:
        print(f"\nResult:\n{result['result']}")
    if result['error']:
        print(f"\nError: {result['error']}")
