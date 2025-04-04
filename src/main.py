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
        port = int(os.getenv('PORT'))
        logger.info(f"Starting server on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()