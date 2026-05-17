"""
Web Interface for Agentic Platform
Provides real-time visualization of agent execution via SSE
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import logging

from agentic_platform import (
    AgenticPlatform, 
    Task, 
    TaskStatus, 
    SubAgent,
    LLMClient
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Agentic Platform Visualizer")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active executions
active_executions: Dict[str, "ExecutionSession"] = {}


class EventType(str, Enum):
    """Types of events for real-time updates."""
    AGENT_CREATED = "agent_created"
    AGENT_DEACTIVATED = "agent_deactivated"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_RETRYING = "task_retrying"
    SUBTASK_CREATED = "subtask_created"
    DECOMPOSITION_STARTED = "decomposition_started"
    DECOMPOSITION_COMPLETED = "decomposition_completed"
    EVALUATION_STARTED = "evaluation_started"
    EVALUATION_COMPLETED = "evaluation_completed"
    EXECUTION_COMPLETE = "execution_complete"
    ERROR = "error"


@dataclass
class AgentNode:
    """Represents an agent in the visualization tree."""
    id: str
    name: str
    task_description: str
    status: str = "pending"
    depth: int = 0
    attempts: int = 0
    result: Optional[str] = None
    error: Optional[str] = None
    children: List['AgentNode'] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "task_description": self.task_description,
            "status": self.status,
            "depth": self.depth,
            "attempts": self.attempts,
            "result": self.result,
            "error": self.error,
            "children": [child.to_dict() for child in self.children],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class ExecutionSession:
    """Tracks an execution session for visualization."""
    session_id: str
    goal: str
    requirements: List[str]
    root_agent: Optional[AgentNode] = None
    status: str = "running"
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None
    total_agents: int = 0
    completed_agents: int = 0
    failed_agents: int = 0
    max_depth: int = 0
    events: List[Dict] = field(default_factory=list)
    
    def add_event(self, event_type: EventType, data: Dict):
        """Add an event to the session."""
        event = {
            "type": event_type.value,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.events.append(event)
        logger.info(f"Event: {event_type.value} - {data.get('agent_id', 'N/A')}")
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "goal": self.goal,
            "requirements": self.requirements,
            "root_agent": self.root_agent.to_dict() if self.root_agent else None,
            "status": self.status,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_agents": self.total_agents,
            "completed_agents": self.completed_agents,
            "failed_agents": self.failed_agents,
            "max_depth": self.max_depth,
            "events": self.events[-50:],  # Last 50 events
        }


class VisualizableSubAgent(SubAgent):
    """Extended SubAgent that emits visualization events."""
    
    def __init__(self, *args, session: ExecutionSession = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = session
        self.visual_node = AgentNode(
            id=self.id,
            name=f"Agent-{self.id[:8]}",
            task_description=self.task.description,
            depth=self.depth,
        )
        
        if self.session:
            self.session.add_event(EventType.AGENT_CREATED, {
                "agent_id": self.id,
                "task": self.task.description,
                "depth": self.depth,
            })
    
    async def decompose_task(self) -> List[Task]:
        """Override to add visualization events."""
        if self.session:
            self.session.add_event(EventType.DECOMPOSITION_STARTED, {
                "agent_id": self.id,
                "task": self.task.description,
            })
        
        subtasks = await super().decompose_task()
        
        if self.session and subtasks:
            self.session.add_event(EventType.DECOMPOSITION_COMPLETED, {
                "agent_id": self.id,
                "num_subtasks": len(subtasks),
            })
            
            for i, subtask in enumerate(subtasks):
                self.session.add_event(EventType.SUBTASK_CREATED, {
                    "parent_agent_id": self.id,
                    "subtask_id": subtask.id,
                    "description": subtask.description,
                    "index": i,
                })
        
        return subtasks
    
    async def execute_task(self) -> bool:
        """Override to add visualization events."""
        if self.session:
            self.session.total_agents += 1
            self.session.max_depth = max(self.session.max_depth, self.depth)
            self.visual_node.status = "in_progress"
            self.session.add_event(EventType.TASK_STARTED, {
                "agent_id": self.id,
                "task": self.task.description,
                "attempt": self.task.attempts + 1,
            })
        
        result = await super().execute_task()
        
        if self.session:
            if result:
                self.visual_node.status = "completed"
                self.session.completed_agents += 1
                self.session.add_event(EventType.TASK_COMPLETED, {
                    "agent_id": self.id,
                    "task": self.task.description,
                    "result": str(self.task.result)[:200] if self.task.result else None,
                })
            else:
                self.visual_node.status = "failed"
                self.session.failed_agents += 1
                self.session.add_event(EventType.TASK_FAILED, {
                    "agent_id": self.id,
                    "task": self.task.description,
                    "error": self.task.error,
                })
            
            self.visual_node.attempts = self.task.attempts
            self.visual_node.result = str(self.task.result)[:500] if self.task.result else None
            self.visual_node.error = self.task.error
            self.visual_node.updated_at = datetime.now().isoformat()
        
        return result
    
    async def _execute_with_decomposition(self) -> bool:
        """Override to track child agents in visualization."""
        success = await super()._execute_with_decomposition()
        
        if self.session and self.sub_agents:
            # Add child nodes to visual tree
            for sub_agent in self.sub_agents:
                if isinstance(sub_agent, VisualizableSubAgent):
                    self.visual_node.children.append(sub_agent.visual_node)
        
        return success


class VisualizablePlatform(AgenticPlatform):
    """Extended platform that creates visualizable agents."""
    
    async def execute_with_visualization(
        self, 
        goal: str, 
        requirements: Optional[List[str]] = None,
        session: ExecutionSession = None
    ) -> Dict[str, Any]:
        """Execute with real-time visualization support."""
        logger.info(f"Starting visualized execution of goal: {goal}")
        
        root_task = Task(
            description=goal,
            requirements=requirements or [],
            max_attempts=self.max_retries
        )
        
        root_agent = VisualizableSubAgent(
            llm_client=self.llm_client,
            task=root_task,
            depth=0,
            max_depth=self.max_depth,
            max_retries=self.max_retries,
            session=session
        )
        
        if session:
            session.root_agent = root_agent.visual_node
        
        self.active_agents.append(root_agent)
        
        start_time = asyncio.get_event_loop().time()
        success = await root_agent.execute_task()
        end_time = asyncio.get_event_loop().time()
        
        root_agent.deactivate()
        
        if session:
            session.status = "completed" if success else "failed"
            session.end_time = datetime.now().isoformat()
            session.add_event(EventType.EXECUTION_COMPLETE, {
                "success": success,
                "execution_time": end_time - start_time,
            })
        
        result = {
            "success": success,
            "goal": goal,
            "result": root_task.result,
            "error": root_task.error,
            "attempts": root_task.attempts,
            "execution_time": end_time - start_time,
            "max_depth_reached": self._get_max_depth_reached(root_agent),
            "total_subagents": self._count_subagents(root_agent),
        }
        
        logger.info(f"Execution completed: {'SUCCESS' if success else 'FAILED'}")
        return result


@app.get("/", response_class=HTMLResponse)
async def get_interface():
    """Serve the main visualization interface."""
    return HTMLResponse(content=get_html_template())


@app.post("/api/execute")
async def start_execution(request: Request):
    """Start a new execution session."""
    data = await request.json()
    goal = data.get("goal", "")
    requirements = data.get("requirements", [])
    api_key = data.get("api_key", "")
    model = data.get("model", "deepseek-chat")
    provider = data.get("provider", "deepseek")
    base_url = data.get("base_url", None)
    max_depth = data.get("max_depth", 3)
    max_retries = data.get("max_retries", 5)
    use_mock = data.get("use_mock", not api_key)
    
    if not goal:
        return {"error": "Goal is required"}
    
    session_id = str(uuid.uuid4())
    session = ExecutionSession(
        session_id=session_id,
        goal=goal,
        requirements=requirements,
    )
    active_executions[session_id] = session
    
    # Start execution in background
    asyncio.create_task(run_execution(
        session, 
        api_key, 
        model, 
        provider, 
        base_url, 
        max_depth, 
        max_retries, 
        use_mock
    ))
    
    return {"session_id": session_id, "status": "started"}


async def run_execution(
    session: ExecutionSession,
    api_key: str,
    model: str,
    provider: str,
    base_url: Optional[str],
    max_depth: int,
    max_retries: int,
    use_mock: bool
):
    """Run the actual execution in background."""
    try:
        platform = VisualizablePlatform(
            api_key=api_key if not use_mock else None,
            model=model,
            max_depth=max_depth,
            max_retries=max_retries,
            use_mock=use_mock,
            base_url=base_url,
            provider=provider,
        )
        
        await platform.execute_with_visualization(
            goal=session.goal,
            requirements=session.requirements,
            session=session
        )
    except Exception as e:
        logger.error(f"Execution error: {e}")
        session.status = "error"
        session.end_time = datetime.now().isoformat()
        session.add_event(EventType.ERROR, {
            "message": str(e),
        })


@app.get("/api/sse/{session_id}")
async def stream_events(session_id: str):
    """Stream real-time events for a session."""
    async def event_generator():
        last_event_count = 0
        
        while True:
            if session_id not in active_executions:
                yield {
                    "event": "session_ended",
                    "data": json.dumps({"reason": "Session not found"})
                }
                break
            
            session = active_executions[session_id]
            
            # Send new events
            if len(session.events) > last_event_count:
                new_events = session.events[last_event_count:]
                for event in new_events:
                    yield {
                        "event": event["type"],
                        "data": json.dumps(event)
                    }
                last_event_count = len(session.events)
            
            # Send session state update
            yield {
                "event": "state_update",
                "data": json.dumps(session.to_dict())
            }
            
            # Stop if session is complete
            if session.status in ["completed", "failed", "error"]:
                yield {
                    "event": "session_ended",
                    "data": json.dumps(session.to_dict())
                }
                break
            
            await asyncio.sleep(0.5)
    
    return EventSourceResponse(event_generator())


@app.get("/api/session/{session_id}")
async def get_session_status(session_id: str):
    """Get current status of a session."""
    if session_id not in active_executions:
        return {"error": "Session not found"}, 404
    
    session = active_executions[session_id]
    return session.to_dict()


def get_html_template() -> str:
    """Return the HTML template for the visualization interface."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agentic Platform Visualizer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .form-card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        input, textarea, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        textarea {
            resize: vertical;
            min-height: 100px;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }
        
        .panel {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            max-height: 600px;
            overflow-y: auto;
        }
        
        .panel h2 {
            color: #667eea;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .agent-tree {
            font-family: 'Courier New', monospace;
            font-size: 13px;
        }
        
        .agent-node {
            padding: 10px;
            margin: 5px 0;
            border-radius: 6px;
            border-left: 4px solid #ccc;
            background: #f9f9f9;
        }
        
        .agent-node.pending {
            border-left-color: #ffc107;
            background: #fff8e1;
        }
        
        .agent-node.in_progress {
            border-left-color: #2196f3;
            background: #e3f2fd;
            animation: pulse 1.5s infinite;
        }
        
        .agent-node.completed {
            border-left-color: #4caf50;
            background: #e8f5e9;
        }
        
        .agent-node.failed {
            border-left-color: #f44336;
            background: #ffebee;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .event-log {
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }
        
        .event-item {
            padding: 8px;
            margin: 5px 0;
            border-radius: 4px;
            background: #f5f5f5;
            border-left: 3px solid #667eea;
        }
        
        .event-item.error {
            border-left-color: #f44336;
            background: #ffebee;
        }
        
        .event-item.success {
            border-left-color: #4caf50;
            background: #e8f5e9;
        }
        
        .event-timestamp {
            color: #666;
            font-size: 11px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
        }
        
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .hidden {
            display: none;
        }
        
        .advanced-options {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 2px solid #f0f0f0;
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .checkbox-group input {
            width: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Agentic Platform Visualizer</h1>
        
        <div class="form-card">
            <div class="form-group">
                <label for="goal">Goal / Problem to Solve:</label>
                <textarea id="goal" placeholder="E.g., Create a Python web scraper that extracts weather data from multiple sources"></textarea>
            </div>
            
            <div class="form-group">
                <label for="requirements">Requirements (one per line):</label>
                <textarea id="requirements" placeholder="- Must handle errors gracefully&#10;- Should save data to CSV&#10;- Include logging" style="min-height: 80px;"></textarea>
            </div>
            
            <div class="form-group">
                <label for="provider">LLM Provider:</label>
                <select id="provider" onchange="toggleProviderOptions()">
                    <option value="deepseek">DeepSeek</option>
                    <option value="openai">OpenAI</option>
                    <option value="custom">Custom Endpoint</option>
                    <option value="mock">Mock (Testing)</option>
                </select>
            </div>
            
            <div class="form-group" id="apiKeyGroup">
                <label for="apiKey">API Key:</label>
                <input type="password" id="apiKey" placeholder="Enter your API key">
            </div>
            
            <div class="form-group" id="modelGroup">
                <label for="model">Model:</label>
                <input type="text" id="model" value="deepseek-chat" placeholder="E.g., deepseek-chat, gpt-4">
            </div>
            
            <div class="form-group hidden" id="baseUrlGroup">
                <label for="baseUrl">Custom Base URL:</label>
                <input type="text" id="baseUrl" placeholder="E.g., http://localhost:11434/v1">
            </div>
            
            <div class="advanced-options">
                <div class="stats-grid" style="grid-template-columns: repeat(3, 1fr);">
                    <div class="form-group">
                        <label for="maxDepth">Max Depth:</label>
                        <input type="number" id="maxDepth" value="3" min="1" max="10">
                    </div>
                    
                    <div class="form-group">
                        <label for="maxRetries">Max Retries:</label>
                        <input type="number" id="maxRetries" value="5" min="1" max="10">
                    </div>
                    
                    <div class="form-group checkbox-group">
                        <input type="checkbox" id="useMock">
                        <label for="useMock" style="margin: 0;">Use Mock Mode</label>
                    </div>
                </div>
            </div>
            
            <button class="btn" onclick="startExecution()" id="startBtn">🚀 Start Execution</button>
        </div>
        
        <div id="dashboard" class="dashboard hidden">
            <div class="panel">
                <h2>📊 Statistics</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value" id="totalAgents">0</div>
                        <div class="stat-label">Total Agents</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="completedAgents">0</div>
                        <div class="stat-label">Completed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="failedAgents">0</div>
                        <div class="stat-label">Failed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="maxDepth">0</div>
                        <div class="stat-label">Max Depth</div>
                    </div>
                </div>
                
                <h2>🌳 Agent Tree</h2>
                <div id="agentTree" class="agent-tree"></div>
            </div>
            
            <div class="panel">
                <h2>📝 Event Log</h2>
                <div id="eventLog" class="event-log"></div>
            </div>
        </div>
    </div>
    
    <script>
        let currentSessionId = null;
        let eventSource = null;
        
        function toggleProviderOptions() {
            const provider = document.getElementById('provider').value;
            const apiKeyGroup = document.getElementById('apiKeyGroup');
            const baseUrlGroup = document.getElementById('baseUrlGroup');
            const useMock = document.getElementById('useMock');
            
            if (provider === 'mock') {
                useMock.checked = true;
                apiKeyGroup.classList.add('hidden');
                baseUrlGroup.classList.add('hidden');
            } else if (provider === 'custom') {
                apiKeyGroup.classList.remove('hidden');
                baseUrlGroup.classList.remove('hidden');
            } else {
                apiKeyGroup.classList.remove('hidden');
                baseUrlGroup.classList.add('hidden');
            }
        }
        
        function parseRequirements() {
            const text = document.getElementById('requirements').value;
            return text.split('\\n')
                .map(r => r.trim())
                .filter(r => r.length > 0)
                .map(r => r.replace(/^[-•*]\\s*/, ''));
        }
        
        async function startExecution() {
            const goal = document.getElementById('goal').value.trim();
            if (!goal) {
                alert('Please enter a goal');
                return;
            }
            
            const provider = document.getElementById('provider').value;
            const useMock = document.getElementById('useMock').checked || provider === 'mock';
            
            const payload = {
                goal: goal,
                requirements: parseRequirements(),
                provider: provider === 'mock' ? 'deepseek' : provider,
                api_key: document.getElementById('apiKey').value,
                model: document.getElementById('model').value,
                base_url: document.getElementById('baseUrl').value || null,
                max_depth: parseInt(document.getElementById('maxDepth').value),
                max_retries: parseInt(document.getElementById('maxRetries').value),
                use_mock: useMock
            };
            
            const btn = document.getElementById('startBtn');
            btn.disabled = true;
            btn.textContent = '⏳ Starting...';
            
            try {
                const response = await fetch('/api/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                
                const data = await response.json();
                currentSessionId = data.session_id;
                
                document.getElementById('dashboard').classList.remove('hidden');
                connectToSSE(currentSessionId);
                
                btn.textContent = '🔄 Running...';
            } catch (error) {
                alert('Error starting execution: ' + error.message);
                btn.disabled = false;
                btn.textContent = '🚀 Start Execution';
            }
        }
        
        function connectToSSE(sessionId) {
            if (eventSource) {
                eventSource.close();
            }
            
            eventSource = new EventSource('/api/sse/' + sessionId);
            
            eventSource.addEventListener('state_update', (event) => {
                const state = JSON.parse(event.data);
                updateDashboard(state);
            });
            
            eventSource.addEventListener('agent_created', (event) => {
                const data = JSON.parse(event.data);
                addEventToLog('Agent Created', `Agent ${data.agent_id.substring(0, 8)}... at depth ${data.depth}`, 'info');
            });
            
            eventSource.addEventListener('task_started', (event) => {
                const data = JSON.parse(event.data);
                addEventToLog('Task Started', `Agent ${data.agent_id.substring(0, 8)}... attempting task (Attempt ${data.attempt})`, 'info');
            });
            
            eventSource.addEventListener('task_completed', (event) => {
                const data = JSON.parse(event.data);
                addEventToLog('Task Completed', `Agent ${data.agent_id.substring(0, 8)}... succeeded`, 'success');
            });
            
            eventSource.addEventListener('task_failed', (event) => {
                const data = JSON.parse(event.data);
                addEventToLog('Task Failed', `Agent ${data.agent_id.substring(0, 8)}... failed: ${data.error}`, 'error');
            });
            
            eventSource.addEventListener('decomposition_started', (event) => {
                const data = JSON.parse(event.data);
                addEventToLog('Decomposition', `Agent ${data.agent_id.substring(0, 8)}... breaking down task`, 'info');
            });
            
            eventSource.addEventListener('subtask_created', (event) => {
                const data = JSON.parse(event.data);
                addEventToLog('Subtask', `Created subtask ${data.index + 1}: ${data.description.substring(0, 50)}...`, 'info');
            });
            
            eventSource.addEventListener('execution_complete', (event) => {
                const data = JSON.parse(event.data);
                const message = data.success ? '✅ Execution completed successfully!' : '❌ Execution failed';
                addEventToLog('Complete', message, data.success ? 'success' : 'error');
                
                const btn = document.getElementById('startBtn');
                btn.disabled = false;
                btn.textContent = '🚀 Start Execution';
                
                eventSource.close();
            });
            
            eventSource.addEventListener('session_ended', (event) => {
                eventSource.close();
            });
            
            eventSource.onerror = (error) => {
                console.error('SSE Error:', error);
                addEventToLog('Error', 'Connection lost', 'error');
                eventSource.close();
            };
        }
        
        function updateDashboard(state) {
            document.getElementById('totalAgents').textContent = state.total_agents;
            document.getElementById('completedAgents').textContent = state.completed_agents;
            document.getElementById('failedAgents').textContent = state.failed_agents;
            document.getElementById('maxDepth').textContent = state.max_depth;
            
            if (state.root_agent) {
                renderAgentTree(state.root_agent);
            }
        }
        
        function renderAgentTree(node, indent = 0) {
            const container = document.getElementById('agentTree');
            const statusClass = node.status.replace('_', '-');
            
            const html = `
                <div class="agent-node ${statusClass}" style="margin-left: ${indent * 20}px;">
                    <strong>${node.name}</strong><br>
                    <small>${node.task_description.substring(0, 80)}${node.task_description.length > 80 ? '...' : ''}</small><br>
                    <small>Status: ${node.status} | Attempts: ${node.attempts}</small>
                    ${node.error ? `<br><small style="color: red;">Error: ${node.error.substring(0, 50)}</small>` : ''}
                </div>
            `;
            
            container.innerHTML += html;
            
            if (node.children && node.children.length > 0) {
                node.children.forEach(child => renderAgentTree(child, indent + 1));
            }
        }
        
        function addEventToLog(type, message, level = 'info') {
            const container = document.getElementById('eventLog');
            const timestamp = new Date().toLocaleTimeString();
            
            const html = `
                <div class="event-item ${level}">
                    <div class="event-timestamp">${timestamp}</div>
                    <strong>[${type}]</strong> ${message}
                </div>
            `;
            
            container.innerHTML = html + container.innerHTML;
            
            // Keep only last 100 events
            while (container.children.length > 100) {
                container.removeChild(container.lastChild);
            }
        }
    </script>
</body>
</html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
