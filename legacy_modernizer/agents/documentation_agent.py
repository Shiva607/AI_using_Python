# agents/documentation_agent.py

from core.llm_client import LLMClient
from core.ir_schema import ProjectIR
from prompts.documentation_prompt import (
    DOCUMENTATION_SYSTEM_PROMPT,
    create_documentation_prompt
)
import json


class DocumentationAgent:
    def __init__(self):
        self.llm = LLMClient()
    
    def generate_structured_analysis(self, code: str, language: str, filename: str = "unknown") -> ProjectIR:
        """
        Generate validated IR from legacy code
        
        Args:
            code: Source code to analyze
            language: Programming language
            filename: Original filename
        
        Returns:
            ProjectIR: Validated Pydantic model
        
        Raises:
            ValueError: If LLM output doesn't match schema
            RuntimeError: If LLM call fails
        """
        user_prompt = create_documentation_prompt(code, language, filename)
        
        # Get LLM response
        raw_response = self.llm.generate(
            system_prompt=DOCUMENTATION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0
        )
        
        # Clean the response
        cleaned_json = self._clean_json_response(raw_response)
        
        # Validate against schema
        try:
            project_ir = ProjectIR.model_validate_json(cleaned_json)
            return project_ir
        except Exception as e:
            raise ValueError(f"LLM output failed schema validation: {str(e)}\n\nRaw output:\n{raw_response[:500]}")
    
    def _clean_json_response(self, response: str) -> str:
        """
        Clean LLM response to extract pure JSON
        """
        response = response.strip()
        
        # Remove markdown code fences
        if response.startswith('```'):
            lines = response.split('\n')
            # Remove first line (```json or ```)
            lines = lines[1:]
            # Remove last line (```)
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            response = '\n'.join(lines)
        
        # Validate it's actually JSON
        try:
            json.loads(response)
            return response
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM did not return valid JSON: {str(e)}")
    
    def generate_markdown_from_ir(self, ir: ProjectIR) -> str:
        """
        Convert validated IR to human-readable markdown documentation
        """
        sections = []
        
        # Header
        sections.append(f"# {ir.language.upper()} Code Analysis\n")
        sections.append(f"**Original File:** `{ir.original_filename}`  ")
        sections.append(f"**Suggested Modern Name:** `{ir.suggested_filename}`\n")
        sections.append(f"## Project Summary\n{ir.summary}\n")
        
        # Modules
        sections.append("## Architecture Overview\n")
        for module in ir.modules:
            sections.append(f"### {module.type.title()}: `{module.name}`\n")
            sections.append(f"{module.description}\n")
            
            if module.design_patterns:
                sections.append(f"**Design Patterns:** {', '.join(module.design_patterns)}\n")
            
            if module.attributes:
                sections.append("**Attributes:**\n")
                for attr in module.attributes:
                    sections.append(f"- `{attr.type} {attr.name}`: {attr.description or 'N/A'}\n")
            
            # Functions
            if module.functions:
                sections.append(f"\n#### Methods ({len(module.functions)} total)\n")
                
                for func in module.functions:
                    sections.append(f"\n##### `{func.name}`\n")
                    sections.append(f"{func.description}\n")
                    
                    # Signature
                    if func.modifiers:
                        sections.append(f"**Modifiers:** {', '.join(func.modifiers)}\n")
                    
                    if func.inputs:
                        sections.append("**Parameters:**\n")
                        for inp in func.inputs:
                            sections.append(f"- `{inp.type} {inp.name}`: {inp.description or 'N/A'}\n")
                    
                    if func.outputs:
                        sections.append("**Returns:**\n")
                        for out in func.outputs:
                            sections.append(f"- `{out.type}`: {out.description or 'N/A'}\n")
                    
                    if func.business_logic:
                        sections.append(f"**Business Logic:** {func.business_logic}\n")
                    
                    if func.side_effects:
                        sections.append(f"**Side Effects:** {', '.join(func.side_effects)}\n")
                    
                    if func.decisions:
                        sections.append("**Decision Points:**\n")
                        for dec in func.decisions:
                            sections.append(f"- {dec.condition}: {dec.description or 'N/A'}\n")
                    
                    if func.exceptions:
                        sections.append(f"**Exceptions:** {', '.join(func.exceptions)}\n")
                    
                    if func.dependencies:
                        sections.append(f"**Dependencies:** {', '.join(func.dependencies)}\n")
            
            sections.append("\n---\n")
        
        # Technical Debt
        if ir.technical_debt:
            sections.append("## ⚠️ Technical Debt Analysis\n")
            
            by_severity = {"critical": [], "high": [], "medium": [], "low": []}
            for debt in ir.technical_debt:
                by_severity[debt.severity].append(debt)
            
            for severity in ["critical", "high", "medium", "low"]:
                if by_severity[severity]:
                    sections.append(f"\n### {severity.upper()} Priority\n")
                    for debt in by_severity[severity]:
                        sections.append(f"**{debt.category.title()}:** {debt.description}\n")
                        sections.append(f"*Recommendation:* {debt.recommendation}\n\n")
        
        # Modernization Priorities
        if ir.modernization_priority:
            sections.append("## 🚀 Modernization Roadmap\n")
            for i, priority in enumerate(ir.modernization_priority, 1):
                sections.append(f"{i}. {priority}\n")
        
        # Dependencies
        if ir.dependencies:
            sections.append(f"\n## 📦 External Dependencies\n")
            for dep in ir.dependencies:
                sections.append(f"- {dep}\n")
        
        return '\n'.join(sections)
    
    def generate_code_skeleton(self, ir: ProjectIR) -> str:
        """
        Generate code skeleton from IR
        """
        lines = []
        
        for module in ir.modules:
            # Class/Module header
            if ir.language == "java":
                lines.append(f"// {module.description}")
                lines.append(f"// Original: {ir.original_filename}")
                lines.append(f"// Suggested: {ir.suggested_filename}")
                lines.append(f"public class {module.name} {{")
                lines.append("")
                
                # Attributes
                for attr in module.attributes:
                    lines.append(f"    private {attr.type} {attr.name}; // {attr.description or ''}")
                
                if module.attributes:
                    lines.append("")
                
                # Methods
                for func in module.functions:
                    lines.append(f"    // {func.description}")
                    
                    modifiers = ' '.join(func.modifiers) if func.modifiers else "public"
                    return_type = func.outputs[0].type if func.outputs else "void"
                    params = ", ".join([f"{inp.type} {inp.name}" for inp in func.inputs])
                    
                    lines.append(f"    {modifiers} {return_type} {func.name}({params}) {{")
                    
                    if func.business_logic:
                        lines.append(f"        // Logic: {func.business_logic}")
                    
                    lines.append("        // TODO: Implement")
                    
                    if return_type != "void":
                        lines.append(f"        return null;")
                    
                    lines.append("    }")
                    lines.append("")
                
                lines.append("}")
            
            elif ir.language == "python":
                lines.append(f'"""')
                lines.append(f'{module.description}')
                lines.append(f'Original: {ir.original_filename}')
                lines.append(f'Suggested: {ir.suggested_filename}')
                lines.append(f'"""')
                lines.append("")
                
                if module.type == "class":
                    lines.append(f"class {module.name}:")
                    lines.append(f'    """{module.description}"""')
                    lines.append("")
                    
                    # Attributes
                    if module.attributes:
                        lines.append("    def __init__(self):")
                        for attr in module.attributes:
                            lines.append(f"        self.{attr.name}: {attr.type} = None  # {attr.description or ''}")
                        lines.append("")
                    
                    for func in module.functions:
                        params = ", ".join(["self"] + [inp.name for inp in func.inputs])
                        lines.append(f"    def {func.name}({params}):")
                        lines.append(f'        """{func.description}"""')
                        if func.business_logic:
                            lines.append(f"        # Logic: {func.business_logic}")
                        lines.append("        # TODO: Implement")
                        lines.append("        pass")
                        lines.append("")
                else:
                    # Module-level functions
                    for func in module.functions:
                        params = ", ".join([inp.name for inp in func.inputs])
                        lines.append(f"def {func.name}({params}):")
                        lines.append(f'    """{func.description}"""')
                        if func.business_logic:
                            lines.append(f"    # Logic: {func.business_logic}")
                        lines.append("    # TODO: Implement")
                        lines.append("    pass")
                        lines.append("")
            
            elif ir.language == "javascript":
                lines.append(f"// {module.description}")
                lines.append(f"// Original: {ir.original_filename}")
                lines.append(f"// Suggested: {ir.suggested_filename}")
                lines.append("")
                
                if module.type == "class":
                    lines.append(f"class {module.name} {{")
                    
                    for func in module.functions:
                        params = ", ".join([inp.name for inp in func.inputs])
                        lines.append(f"  // {func.description}")
                        lines.append(f"  {func.name}({params}) {{")
                        if func.business_logic:
                            lines.append(f"    // Logic: {func.business_logic}")
                        lines.append("    // TODO: Implement")
                        lines.append("  }")
                        lines.append("")
                    
                    lines.append("}")
                else:
                    for func in module.functions:
                        params = ", ".join([inp.name for inp in func.inputs])
                        lines.append(f"// {func.description}")
                        lines.append(f"function {func.name}({params}) {{")
                        if func.business_logic:
                            lines.append(f"  // Logic: {func.business_logic}")
                        lines.append("  // TODO: Implement")
                        lines.append("}")
                        lines.append("")
        
        return '\n'.join(lines)
    
    def generate_comprehensive_documentation(
        self,
        ir: ProjectIR,
        original_code: str,
        modernized_code: str,
        changes_summary: str
    ) -> dict:
        """
        Generate both master and modular documentation
        """
        from agents.advanced_documentation_agent import AdvancedDocumentationGenerator
        
        generator = AdvancedDocumentationGenerator()
        return generator.generate_master_documentation(
            ir, original_code, modernized_code, changes_summary
        )