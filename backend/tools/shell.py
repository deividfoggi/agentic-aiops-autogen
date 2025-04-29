import subprocess
from utils.config import Config

def shell(command: str) -> str:
    """
    Executa comandos em um shell linux.

    Parâmetros:
    - command (str): Comando a ser executado dentro do AKS. Exemplos: "kubectl get pods", "az login", etc.

    Retorno:
    - str: Saída do comando ou erro.
    """
    try:
        result = subprocess.run(
            command,
            shell=True, check=True, capture_output=True, text=True
        )

        return result.stdout.strip()
    
    except subprocess.CalledProcessError as e:
        return f"Erro ao executar comando: {e.stderr.strip()}"
