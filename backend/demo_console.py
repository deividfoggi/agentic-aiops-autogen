#!/usr/bin/env python3

"""
Simple test script to demonstrate console streaming functionality.
This script creates print statements and log messages that will be 
captured and streamed to the frontend.
"""

import time
import logging
import sys
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def demo_console_output():
    """Demonstrate various types of console output for frontend streaming."""
    
    print("🚀 Demo Console Streaming Started")
    print("=" * 50)
    
    # Standard output
    print("📊 Generating sample output...")
    time.sleep(1)
    
    # Different log levels
    logger.info("This is an INFO log message")
    logger.warning("This is a WARNING log message")
    logger.error("This is an ERROR log message")
    logger.debug("This is a DEBUG log message")
    
    # Simulate processing
    for i in range(1, 6):
        print(f"⏳ Processing step {i}/5...")
        time.sleep(0.5)
    
    # Simulate error to stderr
    print("⚠️ Simulating an error...", file=sys.stderr)
    
    # Success message
    print("✅ Demo completed successfully!")
    print(f"🕐 Finished at: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    demo_console_output()
