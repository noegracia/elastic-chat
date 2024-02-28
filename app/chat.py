from dotenv import load_dotenv
import os
import yaml
from openai import OpenAI

# Load the YAML file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Load environment variables from .env file
load_dotenv("../.env")

# Required Environment Variables
openai_api = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=openai_api)

# Accessing config variables
user = config['user']
model = config['model']
systemPrompt = config['systemPrompt']
negResponse = config['negResponse']

def truncate_text(text, max_tokens):
    tokens = text.split()
    if len(tokens) <= max_tokens:
        return text

    return ' '.join(tokens[:max_tokens])

# Generate a response from ChatGPT based on the given prompt
def chat_gpt(prompt, model="gpt-3.5-turbo", max_tokens=1024, max_context_tokens=4000, safety_margin=5):
    truncated_prompt = truncate_text(prompt, max_context_tokens - max_tokens - safety_margin)
    
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": f"{systemPrompt}"}, {"role": "user", "content": truncated_prompt}],
        max_tokens=max_tokens,
        temperature=0.7  # You might adjust or add other parameters as needed
    )
    
    return completion.choices[0].message.content