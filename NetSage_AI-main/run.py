"""
NetSage AI — Application Entry Point
Single command to start the entire application.
"""

import sys
import os
import io

# Ensure UTF-8 output streams across all platforms
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

import uvicorn

if __name__ == "__main__":
    print("\n* Starting NetSage AI...")
    print("* Web App:  http://localhost:8000")
    print("* API Docs: http://localhost:8000/docs")
    print("* Demo Mode: " + ("Active (no API key)" if not os.getenv("OPENAI_API_KEY") else "Live API key connected"))
    print()

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )
