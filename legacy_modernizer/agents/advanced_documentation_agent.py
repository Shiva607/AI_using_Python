# agents/advanced_documentation_agent.py

from core.ir_schema import ProjectIR
from typing import List
import re


class AdvancedDocumentationGenerator:
    """
    Generates comprehensive migration documentation following
    the Master Code Modernization Prompt structure
    """
    
    def generate_master_documentation(
        self,
        ir: ProjectIR,
        original_code: str,
        modernized_code: str,
        changes_summary: str
    ) -> dict:
        """
        Generate complete migration documentation
        
        Returns:
            dict: {
                "master_doc": str (comprehensive single doc),
                "modular_docs": dict (multiple focused docs)
            }
        """
        # Generate master document
        master_doc = self._generate_master_doc(ir, original_code, modernized_code, changes_summary)
        
        # Generate modular documents
        modular_docs = self._generate_modular_docs(ir, original_code, modernized_code, changes_summary)
        
        return {
            "master_doc": master_doc,
            "modular_docs": modular_docs
        }
    
    def _generate_master_doc(
        self,
        ir: ProjectIR,
        original_code: str,
        modernized_code: str,
        changes_summary: str
    ) -> str:
        """Generate comprehensive single migration document"""
        
        sections = []
        
        # Title
        sections.append(f"# Code Modernization Documentation")
        sections.append(f"## {ir.original_filename} → {ir.suggested_filename}\n")
        sections.append("---\n")
        
        # 1. Metadata & Environment
        sections.append("## 1. Metadata & Environment\n")
        sections.append(f"### Source")
        sections.append(f"- **Language:** {ir.language.upper()}")
        sections.append(f"- **Original File:** `{ir.original_filename}`")
        sections.append(f"- **Legacy Patterns:** {', '.join([d.category for d in ir.technical_debt[:3]])}\n")
        
        sections.append(f"### Target")
        sections.append(f"- **Modern File:** `{ir.suggested_filename}`")
        sections.append(f"- **Target Version:** {self._get_modern_version(ir.language)}")
        sections.append(f"- **Modernization Focus:** {changes_summary}\n")
        
        sections.append(f"### Paradigm Shift")
        sections.append(self._describe_paradigm_shift(ir))
        sections.append("\n---\n")
        
        # 2. Modernized Code Architecture
        sections.append("## 2. Modernized Code Architecture\n")
        sections.append(self._generate_architecture_section(ir))
        sections.append("\n---\n")
        
        # 3. Proposed Folder Structure
        sections.append("## 3. Proposed Folder Structure\n")
        sections.append("```")
        sections.append(self._generate_folder_structure(ir))
        sections.append("```\n")
        sections.append("\n---\n")
        
        # 4. Side-by-Side Comparison
        sections.append("## 4. Legacy vs Modern: Side-by-Side Comparison\n")
        sections.append(self._generate_comparison_table(ir, original_code, modernized_code))
        sections.append("\n---\n")
        
        # 5. Code Comparison
        sections.append("## 5. Complete Code Transformation\n")
        sections.append("### Legacy Code (Before)")
        sections.append(f"```{ir.language}")
        sections.append(original_code[:2000] + ("..." if len(original_code) > 2000 else ""))
        sections.append("```\n")
        
        sections.append("### Modern Code (After)")
        sections.append(f"```{ir.language}")
        sections.append(modernized_code[:2000] + ("..." if len(modernized_code) > 2000 else ""))
        sections.append("```\n")
        sections.append("\n---\n")
        
        # 6. Technical Debt Analysis
        if ir.technical_debt:
            sections.append("## 6. Technical Debt Addressed\n")
            sections.append(self._generate_technical_debt_section(ir))
            sections.append("\n---\n")
        
        # 7. Execution Guide
        sections.append("## 7. Execution Guide\n")
        sections.append(self._generate_execution_guide(ir))
        sections.append("\n---\n")
        
        # 8. Validation Checklist
        sections.append("## 8. Validation Checklist\n")
        sections.append(self._generate_validation_checklist(ir))
        sections.append("\n---\n")
        
        # 9. Modernization Roadmap
        if ir.modernization_priority:
            sections.append("## 9. Modernization Roadmap\n")
            for i, priority in enumerate(ir.modernization_priority, 1):
                sections.append(f"{i}. {priority}")
            sections.append("\n---\n")
        
        # Footer
        sections.append("\n## Summary\n")
        sections.append(f"**Total Modules:** {len(ir.modules)}")
        sections.append(f"**Total Functions:** {sum(len(m.functions) for m in ir.modules)}")
        sections.append(f"**Technical Debt Items:** {len(ir.technical_debt)}")
        sections.append(f"**Status:** ✅ Modernization Complete\n")
        
        return '\n'.join(sections)
    
    def _generate_modular_docs(
        self,
        ir: ProjectIR,
        original_code: str,
        modernized_code: str,
        changes_summary: str
    ) -> dict:
        """Generate focused modular documentation files"""
        
        docs = {}
        
        # 1. README.md - Overview
        docs["README.md"] = self._generate_readme(ir, changes_summary)
        
        # 2. ARCHITECTURE.md - Technical details
        docs["ARCHITECTURE.md"] = self._generate_architecture_doc(ir)
        
        # 3. MIGRATION_GUIDE.md - Step-by-step migration
        docs["MIGRATION_GUIDE.md"] = self._generate_migration_guide(ir, original_code, modernized_code)
        
        # 4. TECHNICAL_DEBT.md - Issues and resolutions
        if ir.technical_debt:
            docs["TECHNICAL_DEBT.md"] = self._generate_technical_debt_doc(ir)
        
        # 5. API_REFERENCE.md - Function documentation
        docs["API_REFERENCE.md"] = self._generate_api_reference(ir)
        
        # 6. TESTING_GUIDE.md - Validation and testing
        docs["TESTING_GUIDE.md"] = self._generate_testing_guide(ir)
        
        return docs
    
    def _get_modern_version(self, language: str) -> str:
        """Get target modern version for language"""
        versions = {
            "python": "Python 3.11+",
            "java": "Java 17+ (LTS)",
            "javascript": "ES2022+ / Node.js 18+",
            "typescript": "TypeScript 5.0+",
            "cpp": "C++20",
            "csharp": "C# 11 / .NET 7+"
        }
        return versions.get(language.lower(), f"Modern {language}")
    
    def _describe_paradigm_shift(self, ir: ProjectIR) -> str:
        """Describe the paradigm shift"""
        
        shifts = []
        
        # Check for common patterns
        has_procedural = any("main" in f.name.lower() for m in ir.modules for f in m.functions)
        has_classes = any(m.type == "class" for m in ir.modules)
        
        if has_procedural and not has_classes:
            shifts.append("**From:** Procedural, script-based approach")
            shifts.append("**To:** Modular, object-oriented architecture")
        elif has_classes:
            shifts.append("**From:** Monolithic class structure")
            shifts.append("**To:** Service-oriented, modular design")
        
        shifts.append(f"**Key Changes:** {', '.join([d.category for d in ir.technical_debt[:3]])}")
        
        return '\n'.join(shifts)
    
    def _generate_architecture_section(self, ir: ProjectIR) -> str:
        """Generate architecture section"""
        
        lines = []
        
        lines.append("### Modularization Strategy\n")
        
        for module in ir.modules:
            lines.append(f"#### Module: `{module.name}`")
            lines.append(f"**Type:** {module.type.title()}")
            lines.append(f"**Purpose:** {module.description}")
            lines.append(f"**Functions:** {len(module.functions)}")
            
            if module.design_patterns:
                lines.append(f"**Patterns:** {', '.join(module.design_patterns)}")
            
            lines.append("")
        
        lines.append("### Naming Conventions")
        
        if ir.language == "python":
            lines.append("- **Files:** `snake_case.py`")
            lines.append("- **Classes:** `PascalCase`")
            lines.append("- **Functions:** `snake_case()`")
            lines.append("- **Constants:** `UPPER_SNAKE_CASE`")
        elif ir.language == "java":
            lines.append("- **Files:** `PascalCase.java`")
            lines.append("- **Classes:** `PascalCase`")
            lines.append("- **Methods:** `camelCase()`")
            lines.append("- **Constants:** `UPPER_SNAKE_CASE`")
        elif ir.language in ["javascript", "typescript"]:
            lines.append("- **Files:** `kebab-case.js`")
            lines.append("- **Classes:** `PascalCase`")
            lines.append("- **Functions:** `camelCase()`")
            lines.append("- **Constants:** `UPPER_SNAKE_CASE`")
        
        return '\n'.join(lines)
    
    def _generate_folder_structure(self, ir: ProjectIR) -> str:
        """Generate proposed folder structure"""
        
        if ir.language == "python":
            return """project/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── services/
│   │   └── """ + ir.suggested_filename + """
│   └── utils/
│       └── helpers.py
├── tests/
│   ├── test_services.py
│   └── test_utils.py
├── docs/
│   └── API.md
├── requirements.txt
└── README.md"""
        
        elif ir.language == "java":
            return """project/
├── src/
│   └── main/
│       └── java/
│           └── com/company/
│               ├── """ + ir.suggested_filename + """
│               ├── services/
│               └── utils/
├── src/
│   └── test/
│       └── java/
├── pom.xml
└── README.md"""
        
        elif ir.language in ["javascript", "typescript"]:
            return """project/
├── src/
│   ├── index.js
│   ├── services/
│   │   └── """ + ir.suggested_filename + """
│   └── utils/
│       └── helpers.js
├── tests/
│   └── services.test.js
├── package.json
├── .eslintrc.js
└── README.md"""
        
        else:
            return f"""project/
├── src/
│   └── {ir.suggested_filename}
├── tests/
├── docs/
└── README.md"""
    
    def _generate_comparison_table(self, ir: ProjectIR, original: str, modern: str) -> str:
        """Generate legacy vs modern comparison table"""
        
        lines = []
        lines.append("| Aspect | Legacy Pattern | Modern Pattern | Why? |")
        lines.append("|--------|---------------|----------------|------|")
        
        # Analyze technical debt for comparisons
        for debt in ir.technical_debt[:5]:
            legacy_pattern = debt.description
            modern_pattern = debt.recommendation
            benefit = self._categorize_benefit(debt.category)
            
            lines.append(f"| {debt.category.title()} | {legacy_pattern[:50]} | {modern_pattern[:50]} | {benefit} |")
        
        # Add language-specific patterns
        if ir.language == "python":
            if "print(" in original:
                lines.append("| Logging | `print()` statements | `logging` module | Proper log levels, file output, production-ready |")
        elif ir.language == "java":
            if "Vector" in original:
                lines.append("| Collections | `Vector`, `Hashtable` | `ArrayList`, `HashMap` | Thread-safe by default causes overhead, modern generics |")
        elif ir.language == "javascript":
            if "var " in original:
                lines.append("| Variables | `var` keyword | `const`/`let` | Block scoping, prevents hoisting issues |")
        
        return '\n'.join(lines)
    
    def _categorize_benefit(self, category: str) -> str:
        """Get benefit description for category"""
        benefits = {
            "performance": "⚡ Faster execution, lower memory",
            "security": "🔒 Prevents vulnerabilities",
            "maintainability": "🧹 Easier to read and modify",
            "scalability": "📈 Handles growth better",
            "compatibility": "🔄 Works with modern tools"
        }
        return benefits.get(category, "✨ Improved code quality")
    
    def _generate_execution_guide(self, ir: ProjectIR) -> str:
        """Generate execution guide"""
        
        lines = []
        
        lines.append("### Prerequisites\n")
        
        if ir.language == "python":
            lines.append("```bash")
            lines.append("# Install Python 3.11+")
            lines.append("python --version")
            lines.append("")
            lines.append("# Create virtual environment")
            lines.append("python -m venv venv")
            lines.append("source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
            lines.append("")
            lines.append("# Install dependencies")
            lines.append("pip install -r requirements.txt")
            lines.append("```\n")
            
            lines.append("### Running the Code\n")
            lines.append("```bash")
            lines.append(f"python src/{ir.suggested_filename}")
            lines.append("```")
        
        elif ir.language == "java":
            lines.append("```bash")
            lines.append("# Install Java 17+")
            lines.append("java -version")
            lines.append("")
            lines.append("# Build with Maven")
            lines.append("mvn clean install")
            lines.append("")
            lines.append("# Run")
            lines.append("mvn exec:java")
            lines.append("```")
        
        elif ir.language in ["javascript", "typescript"]:
            lines.append("```bash")
            lines.append("# Install Node.js 18+")
            lines.append("node --version")
            lines.append("")
            lines.append("# Install dependencies")
            lines.append("npm install")
            lines.append("")
            lines.append("# Run")
            lines.append("npm start")
            lines.append("```")
        
        return '\n'.join(lines)
    
    def _generate_validation_checklist(self, ir: ProjectIR) -> str:
        """Generate validation checklist"""
        
        lines = []
        
        lines.append("- [ ] All functions produce identical outputs")
        lines.append("- [ ] No runtime errors or warnings")
        lines.append("- [ ] Unit tests pass (if applicable)")
        lines.append("- [ ] Performance benchmarks meet expectations")
        lines.append("- [ ] Code follows modern style guidelines")
        lines.append("- [ ] Dependencies are up-to-date")
        lines.append("- [ ] Documentation is complete")
        lines.append("- [ ] Security scan passes")
        
        if ir.technical_debt:
            lines.append(f"- [ ] All {len(ir.technical_debt)} technical debt items addressed")
        
        return '\n'.join(lines)
    
    def _generate_technical_debt_section(self, ir: ProjectIR) -> str:
        """Generate technical debt section"""
        
        lines = []
        
        by_severity = {"critical": [], "high": [], "medium": [], "low": []}
        for debt in ir.technical_debt:
            by_severity[debt.severity].append(debt)
        
        for severity in ["critical", "high", "medium", "low"]:
            if by_severity[severity]:
                emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
                lines.append(f"### {emoji[severity]} {severity.upper()} Priority\n")
                
                for debt in by_severity[severity]:
                    lines.append(f"#### {debt.category.title()}")
                    lines.append(f"**Issue:** {debt.description}")
                    lines.append(f"**Resolution:** {debt.recommendation}\n")
        
        return '\n'.join(lines)
    
    # Modular documentation generators
    def _generate_readme(self, ir: ProjectIR, changes_summary: str) -> str:
        """Generate README.md"""
        return f"""# {ir.suggested_filename}

{ir.summary}

## Overview

This is the modernized version of `{ir.original_filename}`.

**Language:** {ir.language.upper()}  
**Target Version:** {self._get_modern_version(ir.language)}

## Changes Summary

{changes_summary}

## Quick Start

See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for detailed setup instructions.

## Documentation

- [Architecture](ARCHITECTURE.md) - System design and structure
- [API Reference](API_REFERENCE.md) - Function documentation
- [Migration Guide](MIGRATION_GUIDE.md) - How to modernize
- [Testing Guide](TESTING_GUIDE.md) - Validation and tests

## Status

✅ Modernization Complete  
📊 Technical Debt Resolved: {len(ir.technical_debt)} items
"""
    
    def _generate_architecture_doc(self, ir: ProjectIR) -> str:
        """Generate ARCHITECTURE.md"""
        return f"""# Architecture Documentation

## System Overview

{ir.summary}

## Module Structure

{self._generate_architecture_section(ir)}

## Design Patterns

{', '.join(set(p for m in ir.modules for p in m.design_patterns)) or 'Standard patterns applied'}

## Dependencies

{chr(10).join(f'- {dep}' for dep in ir.dependencies) or 'No external dependencies'}
"""
    
    def _generate_migration_guide(self, ir: ProjectIR, original: str, modern: str) -> str:
        """Generate MIGRATION_GUIDE.md"""
        return f"""# Migration Guide

## Step-by-Step Modernization

{self._generate_execution_guide(ir)}

## Validation

{self._generate_validation_checklist(ir)}

## Code Comparison

See complete before/after comparison in the master documentation.
"""
    
    def _generate_technical_debt_doc(self, ir: ProjectIR) -> str:
        """Generate TECHNICAL_DEBT.md"""
        return f"""# Technical Debt Analysis

{self._generate_technical_debt_section(ir)}

## Summary

Total Items: {len(ir.technical_debt)}  
Critical: {len([d for d in ir.technical_debt if d.severity == 'critical'])}  
High: {len([d for d in ir.technical_debt if d.severity == 'high'])}
"""
    
    def _generate_api_reference(self, ir: ProjectIR) -> str:
        """Generate API_REFERENCE.md"""
        lines = ["# API Reference\n"]
        
        for module in ir.modules:
            lines.append(f"## {module.name}\n")
            lines.append(f"{module.description}\n")
            
            for func in module.functions:
                lines.append(f"### `{func.name}`\n")
                lines.append(f"{func.description}\n")
                
                if func.inputs:
                    lines.append("**Parameters:**")
                    for inp in func.inputs:
                        lines.append(f"- `{inp.name}` ({inp.type}): {inp.description or 'N/A'}")
                    lines.append("")
                
                if func.outputs:
                    lines.append("**Returns:**")
                    for out in func.outputs:
                        lines.append(f"- {out.type}: {out.description or 'N/A'}")
                    lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_testing_guide(self, ir: ProjectIR) -> str:
        """Generate TESTING_GUIDE.md"""
        return f"""# Testing Guide

## Test Strategy

{self._generate_validation_checklist(ir)}

## Unit Tests

Create tests for each function in the following modules:

{chr(10).join(f'- {m.name} ({len(m.functions)} functions)' for m in ir.modules)}

## Example Test Structure
```{ir.language}
# Add example test code based on language
```
"""