# agents/modernization_agent.py

from core.llm_client import LLMClient
from prompts.modernization_prompt import (
    MODERNIZATION_SYSTEM_PROMPT,
    create_modernization_prompt
)


class ModernizationAgent:
    def __init__(self):
        self.llm = LLMClient()
    
    def modernize_code(self, code: str, language: str) -> str:
        """
        Stage 2: Modernize legacy code
        
        Returns:
            str: Modern, production-ready code
        """
        user_prompt = create_modernization_prompt(code, language)
        
        # LLM-only, let it fail if it fails
        modern_code = self.llm.generate(
            system_prompt=MODERNIZATION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0
        )
        
        # Clean up markdown code fences if present
        modern_code = self._clean_code_output(modern_code)
        
        return modern_code
    
    def _clean_code_output(self, code: str) -> str:
        """
        Remove markdown code fences if present
        """
        lines = code.strip().split('\n')
        
        # Remove opening fence
        if lines[0].startswith('```'):
            lines = lines[1:]
        
        # Remove closing fence
        if lines[-1].startswith('```'):
            lines = lines[:-1]
        
        return '\n'.join(lines)