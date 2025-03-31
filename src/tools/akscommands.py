import subprocess
from utils.config import Config

RESOURCE_GROUP = Config.az_resourcegroup
CLUSTER_NAME = Config.az_aks_name

def execute_aks_command(command: str) -> str:
    """
    Executa um comando kubectl dentro de um cluster AKS.

    Parâmetros:
    - command (str): Comando a ser executado dentro do AKS (ex: "get pods").

    Retorno:
    - str: Saída do comando ou erro.
    """
    try:
        subprocess.run(
            f"az aks get-credentials --resource-group {RESOURCE_GROUP} --name {CLUSTER_NAME} --overwrite-existing",
            shell=True, check=True, capture_output=True, text=True
        )

        result = subprocess.run(
            f"kubectl {command}",
            shell=True, check=True, capture_output=True, text=True
        )

        return result.stdout.strip()
    
    except subprocess.CalledProcessError as e:
        return f"Erro ao executar comando: {e.stderr.strip()}"
