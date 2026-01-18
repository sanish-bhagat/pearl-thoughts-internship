"""Analysis and dependency models."""

from typing import List, Dict, Set, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class DependencyType(str, Enum):
    """Type of dependency relationship."""
    IMPORT = "import"  # File imports from another
    CALL = "call"  # Function/class from another file is called
    INHERIT = "inherit"  # Class inherits from another file
    REFERENCE = "reference"  # Other references (variables, etc.)


@dataclass
class FileDependency:
    """Represents a dependency from one file to another."""
    source_file: str
    target_file: str
    dependency_type: DependencyType
    details: Dict[str, Any] = field(default_factory=dict)  # What specifically is used
    strength: float = 1.0  # 0.0 to 1.0, how strong the dependency is


@dataclass
class RiskScore:
    """Risk assessment for a file."""
    overall_score: float  # 0.0 to 1.0
    factors: Dict[str, float] = field(default_factory=dict)  # Individual risk factors
    explanation: str = ""


@dataclass
class FileAnalysis:
    """Complete analysis for a single file."""
    file_path: str
    dependencies: List[FileDependency] = field(default_factory=list)  # Files this depends on
    dependents: List[str] = field(default_factory=list)  # Files that depend on this
    complexity_metrics: Dict[str, float] = field(default_factory=dict)  # Lines, nesting, etc.
    risk_score: Optional[RiskScore] = None
    function_usage: Dict[str, Set[str]] = field(default_factory=dict)  # func_name -> {files that use it}
    class_usage: Dict[str, Set[str]] = field(default_factory=dict)  # class_name -> {files that use it}
    
    def get_impact_score(self) -> float:
        """Calculate impact: how many files are affected by changes here."""
        return len(self.dependents) / max(1, len(self.dependencies) + len(self.dependents))


@dataclass
class CodebaseAnalysis:
    """Complete analysis of the entire codebase."""
    files: Dict[str, FileAnalysis] = field(default_factory=dict)  # file_path -> FileAnalysis
    dependency_graph: Dict[str, Set[str]] = field(default_factory=dict)  # file -> {dependencies}
    reverse_dependency_graph: Dict[str, Set[str]] = field(default_factory=dict)  # file -> {dependents}
    total_files: int = 0
    total_lines: int = 0
    most_risky_files: List[str] = field(default_factory=list)  # Sorted by risk
    most_impactful_files: List[str] = field(default_factory=list)  # Sorted by impact
    
    def get_file_analysis(self, file_path: str) -> Optional[FileAnalysis]:
        """Get analysis for a specific file."""
        return self.files.get(file_path)
    
    def get_dependencies(self, file_path: str) -> List[str]:
        """Get all files that the given file depends on."""
        return list(self.dependency_graph.get(file_path, set()))
    
    def get_dependents(self, file_path: str) -> List[str]:
        """Get all files that depend on the given file."""
        return list(self.reverse_dependency_graph.get(file_path, set()))
