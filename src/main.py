import os
from dotenv import load_dotenv
from utils.fastapi import app
import uvicorn

def main():
    uvicorn.run(app, host="0.0.0.0", port=os.getenv('PORT'))

if __name__ == "__main__":
    main()