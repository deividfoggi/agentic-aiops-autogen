import sys
import io
import logging
import asyncio
from contextlib import redirect_stdout, redirect_stderr
from threading import Thread
import traceback
from datetime import datetime

class ConsoleStreamer:
    """Captures all console output and streams it to WebSocket connections."""
    
    def __init__(self):
        self.websockets = set()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.buffer = io.StringIO()
        self.is_capturing = False
        
    def add_websocket(self, websocket):
        """Add a WebSocket connection to receive console output."""
        self.websockets.add(websocket)
        
    def remove_websocket(self, websocket):
        """Remove a WebSocket connection."""
        self.websockets.discard(websocket)
        
    async def send_to_websockets(self, sender, message):
        """Send a message to all connected WebSockets."""
        if not self.websockets:
            return
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        data = {
            "sender": sender,
            "text": message,
            "timestamp": timestamp
        }
        
        # Send to all connected WebSockets
        disconnected = set()
        for websocket in self.websockets.copy():
            try:
                await websocket.send_json(data)
            except Exception as e:
                # Mark for removal if WebSocket is disconnected
                disconnected.add(websocket)
                
        # Remove disconnected WebSockets
        for ws in disconnected:
            self.websockets.discard(ws)
    
    def start_capturing(self, websocket):
        """Start capturing console output and stream to WebSocket."""
        self.add_websocket(websocket)
        
        if not self.is_capturing:
            self.is_capturing = True
            
            # Replace stdout and stderr with custom writers
            sys.stdout = ConsoleWriter(self, "STDOUT")
            sys.stderr = ConsoleWriter(self, "STDERR")
            
            # Set up logging handler to capture log messages
            self.setup_logging_handler()
    
    def stop_capturing(self, websocket):
        """Stop capturing for a specific WebSocket."""
        self.remove_websocket(websocket)
        
        # If no more WebSockets, restore original streams
        if not self.websockets and self.is_capturing:
            sys.stdout = self.original_stdout
            sys.stderr = self.original_stderr
            self.is_capturing = False
            
            # Remove logging handler
            self.remove_logging_handler()
    
    def setup_logging_handler(self):
        """Set up a custom logging handler to capture log messages."""
        self.log_handler = WebSocketLogHandler(self)
        
        # Add handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(self.log_handler)
        
        # Also add to specific loggers that might be used
        for logger_name in ['uvicorn', 'fastapi', '__main__']:
            logger = logging.getLogger(logger_name)
            logger.addHandler(self.log_handler)
    
    def remove_logging_handler(self):
        """Remove the custom logging handler."""
        if hasattr(self, 'log_handler'):
            root_logger = logging.getLogger()
            root_logger.removeHandler(self.log_handler)
            
            for logger_name in ['uvicorn', 'fastapi', '__main__']:
                logger = logging.getLogger(logger_name)
                logger.removeHandler(self.log_handler)


class ConsoleWriter:
    """Custom writer that captures output and sends to WebSocket."""
    
    def __init__(self, streamer, stream_type):
        self.streamer = streamer
        self.stream_type = stream_type
        self.original = sys.stdout if stream_type == "STDOUT" else sys.stderr
        
    def write(self, text):
        # Write to original stream
        self.original.write(text)
        self.original.flush()
        
        # Send to WebSockets if there's actual content
        if text.strip():
            # Create async task to send to WebSockets
            asyncio.create_task(
                self.streamer.send_to_websockets(self.stream_type, text.strip())
            )
        
        return len(text)
    
    def flush(self):
        self.original.flush()


class WebSocketLogHandler(logging.Handler):
    """Custom logging handler that sends log messages to WebSocket."""
    
    def __init__(self, streamer):
        super().__init__()
        self.streamer = streamer
        
    def emit(self, record):
        try:
            # Format the log message
            message = self.format(record)
            
            # Determine the log level for sender identification
            sender = f"LOG_{record.levelname}"
            
            # Send to WebSockets
            asyncio.create_task(
                self.streamer.send_to_websockets(sender, message)
            )
        except Exception:
            # Don't let logging errors crash the application
            pass


# Global instance
console_streamer = ConsoleStreamer()
