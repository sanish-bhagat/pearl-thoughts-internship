"""AST-derived data models for code structure."""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class NodeType(str, Enum):
    """Type of AST node."""
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    VARIABLE = "variable"
    IMPORT = "import"


@dataclass
class FunctionNode:
    """Represents a function or method in the code."""
    name: str
    line_start: int
    line_end: int
    parameters: List[str] = field(default_factory=list)
    return_annotation: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    is_async: bool = False
    is_method: bool = False  # True if part of a class
    parent_class: Optional[str] = None  # If method, which class


@dataclass
class ClassNode:
    """Represents a class in the code."""
    name: str
    line_start: int
    line_end: int
    bases: List[str] = field(default_factory=list)  # Parent classes
    decorators: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    methods: List[FunctionNode] = field(default_factory=list)


@dataclass
class ImportNode:
    """Represents an import statement."""
    module: str  # Full module path (e.g., "os.path" or "from os import path")
    alias: Optional[str] = None  # If "import os as o", alias is "o"
    imported_items: List[str] = field(default_factory=list)  # For "from X import a, b"
    import_type: str = "import"  # "import", "from_import", "from_import_all"


@dataclass
class VariableNode:
    """Represents a global variable or constant."""
    name: str
    line: int
    annotation: Optional[str] = None
    value: Optional[str] = None  # String representation of value
    is_constant: bool = False  # True if in ALL_CAPS


@dataclass
class FileASTInfo:
    """Complete AST information for a single file."""
    file_path: str
    language: str = "python"  # Extensible for other languages
    functions: List[FunctionNode] = field(default_factory=list)
    classes: List[ClassNode] = field(default_factory=list)
    imports: List[ImportNode] = field(default_factory=list)
    variables: List[VariableNode] = field(default_factory=list)
    total_lines: int = 0
    code_lines: int = 0  # Excluding comments/blank lines
    parse_error: Optional[str] = None  # If AST parsing failed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "file_path": self.file_path,
            "language": self.language,
            "functions": [
                {
                    "name": f.name,
                    "line_start": f.line_start,
                    "line_end": f.line_end,
                    "parameters": f.parameters,
                    "return_annotation": f.return_annotation,
                    "decorators": f.decorators,
                    "docstring": f.docstring,
                    "is_async": f.is_async,
                    "is_method": f.is_method,
                    "parent_class": f.parent_class,
                }
                for f in self.functions
            ],
            "classes": [
                {
                    "name": c.name,
                    "line_start": c.line_start,
                    "line_end": c.line_end,
                    "bases": c.bases,
                    "decorators": c.decorators,
                    "docstring": c.docstring,
                    "methods": [m.name for m in c.methods],
                }
                for c in self.classes
            ],
            "imports": [
                {
                    "module": i.module,
                    "alias": i.alias,
                    "imported_items": i.imported_items,
                    "import_type": i.import_type,
                }
                for i in self.imports
            ],
            "variables": [
                {
                    "name": v.name,
                    "line": v.line,
                    "annotation": v.annotation,
                    "value": v.value,
                    "is_constant": v.is_constant,
                }
                for v in self.variables
            ],
            "total_lines": self.total_lines,
            "code_lines": self.code_lines,
            "parse_error": self.parse_error,
        }
