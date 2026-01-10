# core/ir_schema.py

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class IOType(BaseModel):
    """Input/Output parameter type"""
    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Data type (e.g., int, String, List[str])")
    description: Optional[str] = Field(None, description="What this parameter represents")


class DecisionPoint(BaseModel):
    """Represents a decision/branch in code"""
    condition: str = Field(..., description="The condition being checked")
    description: Optional[str] = Field(None, description="Business logic explanation")


class FunctionIR(BaseModel):
    """Function/Method intermediate representation"""
    name: str = Field(..., description="Function/method name")
    description: str = Field(..., description="What this function does")
    inputs: List[IOType] = Field(default_factory=list, description="Input parameters")
    outputs: List[IOType] = Field(default_factory=list, description="Return values")
    modifiers: List[str] = Field(default_factory=list, description="Access modifiers (public, private, static, etc.)")
    side_effects: List[str] = Field(default_factory=list, description="Side effects (I/O, state changes, etc.)")
    decisions: List[DecisionPoint] = Field(default_factory=list, description="Conditional logic")
    exceptions: List[str] = Field(default_factory=list, description="Exceptions thrown or handled")
    dependencies: List[str] = Field(default_factory=list, description="External dependencies used")
    business_logic: Optional[str] = Field(None, description="High-level business logic explanation")


class ModuleIR(BaseModel):
    """Class/Module intermediate representation"""
    name: str = Field(..., description="Class or module name")
    type: Literal["class", "module", "interface", "abstract_class"] = Field(..., description="Type of module")
    description: str = Field(..., description="Purpose of this module")
    imports: List[str] = Field(default_factory=list, description="Import statements")
    functions: List[FunctionIR] = Field(default_factory=list, description="Methods/functions in this module")
    attributes: List[IOType] = Field(default_factory=list, description="Class attributes/fields")
    design_patterns: List[str] = Field(default_factory=list, description="Design patterns used")


class TechnicalDebt(BaseModel):
    """Technical debt and issues"""
    category: Literal["performance", "security", "maintainability", "scalability", "compatibility"] = Field(..., description="Issue category")
    description: str = Field(..., description="What the issue is")
    severity: Literal["low", "medium", "high", "critical"] = Field(..., description="How severe")
    recommendation: str = Field(..., description="How to fix it")


class ProjectIR(BaseModel):
    """Complete project intermediate representation"""
    language: str = Field(..., description="Programming language")
    summary: str = Field(..., description="High-level project description")
    modules: List[ModuleIR] = Field(..., description="All classes/modules")
    technical_debt: List[TechnicalDebt] = Field(default_factory=list, description="Issues identified")
    dependencies: List[str] = Field(default_factory=list, description="External libraries/frameworks")
    modernization_priority: List[str] = Field(default_factory=list, description="What to modernize first")
    
    class Config:
        json_schema_extra = {
            "example": {
                "language": "java",
                "summary": "Legacy calculator application",
                "modules": [
                    {
                        "name": "Calculator",
                        "type": "class",
                        "description": "Main calculator class",
                        "functions": [
                            {
                                "name": "add",
                                "description": "Adds two numbers",
                                "inputs": [
                                    {"name": "a", "type": "int", "description": "First number"},
                                    {"name": "b", "type": "int", "description": "Second number"}
                                ],
                                "outputs": [
                                    {"name": "return", "type": "int", "description": "Sum of a and b"}
                                ]
                            }
                        ]
                    }
                ]
            }
        }