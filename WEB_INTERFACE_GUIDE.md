# 🎨 Agentic Platform - Web Interface Guide

## Overview

Your agentic AI platform now has a **beautiful real-time web interface** that lets you visualize everything happening during execution!

## 🚀 Quick Start

### 1. Start the Web Server

```bash
python start_web_interface.py
```

Or directly:

```bash
python web_interface.py
```

### 2. Open Your Browser

Navigate to: **http://localhost:8000**

## ✨ Features

### Real-Time Visualization

- **🌳 Agent Tree**: See the hierarchical structure of agents as they're created
- **📊 Live Statistics**: Track total agents, completed tasks, failures, and max depth
- **📝 Event Log**: Watch every event happen in real-time (agent creation, task execution, decomposition, etc.)
- **🎯 Status Indicators**: Color-coded status for each agent:
  - 🟡 Yellow (Pending) - Waiting to start
  - 🔵 Blue (In Progress) - Currently executing (with pulse animation!)
  - 🟢 Green (Completed) - Successfully finished
  - 🔴 Red (Failed) - Encountered an error

### Configuration Options

The interface lets you configure everything from the browser:

- **Goal/Problem**: Enter any complex problem you want to solve
- **Requirements**: List specific requirements (one per line)
- **LLM Provider**: Choose between:
  - DeepSeek (for deepseek-v4-pro, deepseek-chat, etc.)
  - OpenAI (gpt-4, gpt-3.5-turbo, etc.)
  - Custom Endpoint (Ollama, LM Studio, local servers)
  - Mock Mode (for testing without API calls)
- **API Key**: Securely enter your API key
- **Model Name**: Specify which model to use
- **Custom Base URL**: For local/custom endpoints
- **Max Depth**: Control recursion depth (1-10)
- **Max Retries**: Set retry attempts (1-10)

## 🎯 Example Usage

### Example 1: Using DeepSeek V4 Pro

1. Select "DeepSeek" from provider dropdown
2. Enter your DeepSeek API key
3. Model: `deepseek-v4-pro` or `deepseek-chat`
4. Goal: "Create a Python script that analyzes stock market data"
5. Requirements:
   - Must use pandas for data manipulation
   - Include error handling
   - Generate visualization charts
6. Click "🚀 Start Execution"

### Example 2: Using Local Ollama

1. Select "Custom Endpoint" from provider dropdown
2. Enter API key (can be anything, e.g., "ollama")
3. Model: `llama3` or `mistral`
4. Custom Base URL: `http://localhost:11434/v1`
5. Check "Use Mock Mode" if you want to test without actual API calls
6. Enter your goal and click start

### Example 3: Testing with Mock Mode

1. Select "Mock (Testing)" from provider dropdown
2. No API key needed!
3. Enter any goal to see the interface in action
4. Perfect for understanding how the system works

## 📊 What You'll See

When you start an execution, the dashboard will show:

### Left Panel: Agent Tree & Statistics

```
┌─────────────────────────────────────┐
│ 📊 Statistics                       │
├─────────────────────────────────────┤
│ Total Agents: 7                     │
│ Completed: 5                        │
│ Failed: 0                           │
│ Max Depth: 3                        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 🌳 Agent Tree                       │
├─────────────────────────────────────┤
│ Agent-abcd1234                      │
│ Creating a Python script...         │
│ Status: completed | Attempts: 1     │
│                                     │
│   Agent-ef567890                    │
│   Decompose into modules...         │
│   Status: completed | Attempts: 1   │
│                                     │
│     Agent-12345abc                  │
│     Write main function...          │
│     Status: completed | Attempts: 1 │
└─────────────────────────────────────┘
```

### Right Panel: Event Log

```
┌─────────────────────────────────────┐
│ 📝 Event Log                        │
├─────────────────────────────────────┤
│ 14:32:15 [Complete] ✅ Execution... │
│ 14:32:10 [Task Completed] Agent...  │
│ 14:32:05 [Subtask] Created subta... │
│ 14:32:00 [Decomposition] Agent...   │
│ 14:31:55 [Task Started] Agent...    │
│ 14:31:50 [Agent Created] Agent...   │
└─────────────────────────────────────┘
```

## 🔧 API Endpoints

The web interface exposes these REST APIs:

### POST `/api/execute`
Start a new execution session

```json
{
  "goal": "Your goal here",
  "requirements": ["req1", "req2"],
  "provider": "deepseek",
  "api_key": "your-key",
  "model": "deepseek-chat",
  "max_depth": 3,
  "max_retries": 5,
  "use_mock": false
}
```

Response:
```json
{
  "session_id": "uuid-here",
  "status": "started"
}
```

### GET `/api/sse/{session_id}`
Stream real-time events via Server-Sent Events (SSE)

### GET `/api/session/{session_id}`
Get current session status

## 🎨 Visual Design

The interface features:
- Beautiful gradient background (purple to blue)
- Smooth animations and transitions
- Responsive design that works on different screen sizes
- Color-coded status indicators
- Real-time pulse animation for active agents
- Clean, modern card-based layout
- Monospace fonts for technical information

## 💡 Tips

1. **Start with Mock Mode**: Test the interface without using API credits
2. **Adjust Max Depth**: Lower values (2-3) are faster, higher values (5+) create more detailed breakdowns
3. **Watch the Event Log**: It shows exactly what's happening at each step
4. **Check Agent Tree**: See how tasks are decomposed hierarchically
5. **Use Specific Requirements**: Better requirements lead to better task decomposition

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 8000 is already in use
lsof -i :8000

# Kill the process if needed
kill -9 <PID>

# Or use a different port by editing start_web_interface.py
```

### Can't connect to localhost:8000
- Make sure the server is running
- Check firewall settings
- Try `http://127.0.0.1:8000` instead

### Events not showing
- Check browser console for errors (F12)
- Ensure JavaScript is enabled
- Try a different browser (Chrome, Firefox recommended)

## 📁 Files Created

- `web_interface.py` - Main web interface with FastAPI backend
- `start_web_interface.py` - Easy launcher script
- `server.log` - Server logs (created when running)

## 🔒 Security Notes

- API keys are sent directly to your local server (not stored)
- No data is persisted - everything is in-memory
- For production use, add authentication and HTTPS
- Don't expose this interface publicly without security measures

---

**Enjoy watching your agents work! 🤖✨**
