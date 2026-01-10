# core/llm_client.py

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("OPEN_ROUTER_API_KEY")
        self.model = os.getenv("OPENROUTER_MODEL", "mistralai/devstral-2512:free")
        
        if not self.api_key:
            raise ValueError("OPEN_ROUTER_API_KEY not found in .env file")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key
        )
    
    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0) -> str:
        """
        Centralized LLM call with error handling
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature
            )
            return response.choices[0].message.content
        
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {str(e)}")