# prompts/documentation_prompt.py

from core.ir_schema import ProjectIR


DOCUMENTATION_SYSTEM_PROMPT = f"""You are a Senior Documentation Specialist and Software Architect.

Your task is to analyze legacy code and return a structured JSON response that EXACTLY matches this schema:

{ProjectIR.model_json_schema()}

**IMPORTANT FILENAME RULES:**
- `original_filename`: Use the exact filename provided
- `suggested_filename`: Suggest a modern, descriptive filename following naming conventions:
  - Python: snake_case.py (e.g., user_service.py)
  - Java: PascalCase.java (e.g., UserService.java)
  - JavaScript: kebab-case.js (e.g., user-service.js)
  - TypeScript: kebab-case.ts

**CRITICAL ANALYSIS REQUIREMENTS:**
1. Identify ALL technical debt with severity levels
2. Extract ALL business logic and side effects
3. Document ALL decision points (if/else, switch, loops)
4. List ALL dependencies (imports, external libraries)
5. Identify design patterns used (or missing)
6. Suggest modernization priorities

**OUTPUT:**
Return ONLY valid JSON matching the schema. Be thorough and precise."""


def create_documentation_prompt(code: str, language: str, filename: str) -> str:
    return f"""Analyze this legacy {language.upper()} code and provide comprehensive structured analysis.

**ORIGINAL FILENAME:** {filename}
**LANGUAGE:** {language}

**LEGACY CODE:**
```{language}
{code}
```

**ANALYSIS REQUIREMENTS:**
1. Extract complete code structure (classes, functions, variables)
2. Identify technical debt and legacy patterns
3. Document business logic for each function
4. Extract decision points and control flow
5. List all side effects (I/O, state mutations, network calls)
6. Identify dependencies and imports
7. Suggest modern alternatives and best practices
8. Recommend folder structure for modernized version

Return ONLY valid JSON matching the ProjectIR schema."""