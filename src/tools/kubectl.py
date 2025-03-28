import os
from dotenv import load_dotenv
from utils.httpclient import HttpClient
from autogen_core import CancellationToken
from autogen_core.tools import FunctionTool
from typing_extensions import Annotated
from utils.config import Config
import paramiko
from typing import Optional

load_dotenv()

async def kubectl(command: str, namespace: str, context: str, host: str):
    """Run a kubectl command in the specified namespace and context via SSH."""
    config = Config()
    
    # Get SSH configuration
    ssh_user = "Deivid de Foggi"
    ssh_key_path = config.ssh_key_path
    kubectl_path = "kubectl"
    
    if not all([host, ssh_user, ssh_key_path]):
        raise ValueError("SSH configuration is incomplete. Please check ssh_host, ssh_user, and ssh_key_path in config.")
    
    try:
        # Setup SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect using SSH key
        ssh.connect(
            hostname=host,
            username=ssh_user,
            key_filename=ssh_key_path
        )
        
        # Construct the kubectl command
        cmd = f"{kubectl_path} --context {context} --namespace {namespace} {command}"
        
        # Execute command
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        # Get command output
        response = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        if error:
            raise Exception(f"Command failed: {error}")
        
        return response
        
    except Exception as e:
        raise Exception(f"SSH execution failed: {str(e)}")
        
    finally:
        if 'ssh' in locals():
            ssh.close()

kubectl = FunctionTool(
    kubectl,
    description="Run kubectl commands in an AKS cluster via SSH.",
    name="kubectl",
    strict=True
)