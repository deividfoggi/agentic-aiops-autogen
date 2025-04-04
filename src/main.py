import os
from dotenv import load_dotenv
from utils.fastapi import app
import uvicorn

def main():
    port = int(os.getenv('PORT'))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()