# AIOps Multi-Agents MVP
Multi-agent architecture using Autogen Magentic-One to implement AIOps.

### Architecture overview

The architecture runs the AIOps multi-agents solution in Azure Kubernetes Service as a deployment. The agents use the AKS workload identity model to access resources needed to perform their jobs.

![alt text](media/azure_architecture.png)

## Backend

### Pre-requisites for development
 - VSCode
 - python 3.13.2
 - Docker desktop

### How to run it locally

- Define the following environment variables either in a .env file or directly in the docker run:

   ```
   AZURE_OPENAI_DEPLOYMENT=
   AZURE_OPENAI_MODEL=
   AZURE_OPENAI_API_VERSION=
   AZURE_OPENAI_ENDPOINT=
   AZURE_OPENAI_API_KEY=
   PORT=8000
   LLM_MODEL_SCOPE=https://cognitiveservices.azure.com/.default
   ENVIRONMENT=dev
   ``` 

- Build and run the image:
   ```
   docker build -t mas-app .
   docker run --env-file .env -p 8000:8000 mas-app
   ```

- Send a payload to test it:
   ```
   curl -X POST http://localhost:8000/alert \
   -H "Content-Type: application/json" \
   -d '{"task":"Write a Python script to fetch data from an API."}'
   ```

## Frontend (optional)

### Architecture overview

The frontend is a React-based application designed to interact with the backend services. It provides a user-friendly interface for managing and monitoring the AIOps multi-agents solution.

### Pre-requisites for development
 - Node.js (version 16 or higher)
 - npm or yarn package manager

### How to run it locally

- Navigate to the `frontend` directory:
   ```
   cd frontend
   ```

- Install dependencies:
   ```
   npm install
   ```

- Start the development server:
   ```
   npm start
   ```

- The application will be available at `http://localhost:3000`.