#!/usr/bin/env python3
"""
Start the Agentic Platform Web Interface

Usage:
    python start_web_interface.py
    
Then open http://localhost:8000 in your browser
"""

import uvicorn
from web_interface import app

if __name__ == "__main__":
    print("="*60)
    print("🤖 Agentic Platform Web Interface")
    print("="*60)
    print("\nStarting server at http://localhost:8000")
    print("Open this URL in your browser to access the visualizer\n")
    print("="*60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
