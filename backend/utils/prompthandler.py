# a file that will get a prompt from a file and return it as a string
import os
import json

def get_prompt(prompt_name: str) -> str:
    """
    Get a prompt from a file and return it as a string.
    :param
        prompt_name: The name of the prompt file (without extension).
    :return: The prompt as a string.
    """
    # Get the path to the prompts directory
    prompts_dir = os.path.join(os.path.dirname(__file__), 'prompts')
    
    # Construct the full path to the prompt file
    prompt_file = os.path.join(prompts_dir, f'{prompt_name}.txt')

    # Check if the file exists
    if not os.path.exists(prompt_file):
        raise FileNotFoundError(f"Prompt file '{prompt_file}' not found.")

    # Read the prompt from the file
    with open(prompt_file, 'r', encoding='utf-8') as file:
        prompt_data = file.read()
    
    return prompt_data