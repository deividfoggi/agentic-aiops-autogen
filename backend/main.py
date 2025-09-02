import os
from dotenv import load_dotenv
from utils.fastapi import app
import uvicorn
from utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)

def main():
    try:
        load_dotenv()
        port = int(os.getenv('PORT', 8080))  # Convert to int with default
        
        # Console output that will be streamed to frontend
        print("🚀 AIOps Backend starting up...")
        print(f"📡 Server will run on port {port}")
        print("🔧 Loading environment variables...")
        
        logger.info(f"Starting server on port {port}")
        logger.info("Console streaming enabled - all output will be visible in frontend")
        
        print("✅ Ready to accept connections")
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        print(f"❌ Failed to start application: {str(e)}")
        logger.error(f"Failed to start application: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()