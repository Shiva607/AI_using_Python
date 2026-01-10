# agents/modernization_agent.py

from core.llm_client import LLMClient
from prompts.modernization_prompt import (
    MODERNIZATION_SYSTEM_PROMPT,
    create_modernization_prompt
)
import json


class ModernizationAgent:
    def __init__(self):
        self.llm = LLMClient()
    
    def modernize_code(self, code: str, language: str, original_filename: str, suggested_filename: str) -> dict:
        """
        Modernize legacy code
        
        Args:
            code: Legacy source code
            language: Programming language
            original_filename: Original file name
            suggested_filename: Suggested modern filename from IR
        
        Returns:
            dict: {
                "modernized_code": str,
                "filename": str,
                "changes_summary": str
            }
        """
        user_prompt = create_modernization_prompt(code, language, original_filename, suggested_filename)
        
        # LLM call
        raw_response = self.llm.generate(
            system_prompt=MODERNIZATION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0
        )
        
        # Parse JSON response
        result = self._parse_modernization_response(raw_response)
        return result
    
    def _parse_modernization_response(self, response: str) -> dict:
        """Parse and validate modernization response"""
        response = response.strip()
        
        # Remove markdown fences
        if response.startswith('```'):
            lines = response.split('\n')
            lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            response = '\n'.join(lines)
        
        try:
            result = json.loads(response)
            
            # Validate required fields
            if "modernized_code" not in result:
                raise ValueError("Missing 'modernized_code' field")
            if "filename" not in result:
                result["filename"] = "modernized_code.txt"
            if "changes_summary" not in result:
                result["changes_summary"] = "Code modernized"
            
            return result
        
        except json.JSONDecodeError:
            # Fallback: treat entire response as code
            return {
                "modernized_code": response,
                "filename": "modernized_code.txt",
                "changes_summary": "Modernization completed (no structured response)"
            }