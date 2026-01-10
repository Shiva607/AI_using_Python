# prompts/documentation_prompt.py

from core.ir_schema import ProjectIR


DOCUMENTATION_SYSTEM_PROMPT = f"""You are an expert code analyst.

Your task is to analyze legacy code and return a structured JSON response that EXACTLY matches this schema:

{ProjectIR.model_json_schema()}

**CRITICAL RULES:**
1. Return ONLY valid JSON - no markdown, no explanations, no code fences
2. Every field must match the schema exactly
3. Use null for optional fields if unknown
4. Be thorough in analysis - include all functions, logic, decisions
5. Identify technical debt and modernization needs
6. Explain business logic clearly

**QUALITY CHECKLIST:**
✓ All functions documented with inputs/outputs
✓ Side effects identified (I/O, state changes, network calls)
✓ Decision points extracted (if/else, switch, loops)
✓ Exceptions documented
✓ Dependencies listed
✓ Technical debt categorized by severity
✓ Modernization priorities ranked

Think step-by-step:
1. Identify all classes/modules
2. For each class, identify all methods
3. For each method, extract signature, logic, dependencies
4. Identify patterns and anti-patterns
5. Flag legacy code issues
6. Recommend modernization priorities

Return ONLY the JSON object matching the schema."""


def create_documentation_prompt(code: str, language: str) -> str:
    return f"""Analyze this legacy {language.upper()} code and return structured JSON following the exact schema provided.

**CODE TO ANALYZE:**
```{language}
{code}
```

Return ONLY valid JSON matching the ProjectIR schema. No markdown fences, no explanations."""