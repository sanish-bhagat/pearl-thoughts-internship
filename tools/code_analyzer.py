"""Code analyzer tool for dependency analysis and risk scoring."""

from typing import Dict, List, Set, Optional
from pathlib import Path
from collections import defaultdict

from models.ast_models import FileASTInfo, ImportNode
from models.analysis_models import (
    CodebaseAnalysis,
    FileAnalysis,
    FileDependency,
    DependencyType,
    RiskScore,
)
from models.agent_models import ToolResponse


class CodeAnalyzer:
    """Analyzes codebase structure, dependencies, and risks."""
    
    def __init__(self, scanned_files: Dict[str, FileASTInfo]):
        """
        Initialize the code analyzer.
        
        Args:
            scanned_files: Dictionary of file paths to FileASTInfo objects
        """
        self.scanned_files = scanned_files
        self.root_paths: Set[Path] = set()
        
        # Build root paths set for module resolution
        for file_path in scanned_files.keys():
            path = Path(file_path)
            # Add all parent directories as potential roots
            for parent in path.parents:
                self.root_paths.add(parent)
            self.root_paths.add(path.parent)
    
    def analyze(self) -> ToolResponse:
        """
        Perform full codebase analysis.
        
        Returns:
            ToolResponse with CodebaseAnalysis object
        """
        try:
            analysis = CodebaseAnalysis()
            
            # Build file analysis for each file
            for file_path, ast_info in self.scanned_files.items():
                file_analysis = self._analyze_file(file_path, ast_info)
                analysis.files[file_path] = file_analysis
            
            # Build dependency graphs
            self._build_dependency_graphs(analysis)
            
            # Calculate risk scores
            self._calculate_risk_scores(analysis)
            
            # Sort files by risk and impact
            analysis.most_risky_files = sorted(
                analysis.files.keys(),
                key=lambda f: analysis.files[f].risk_score.overall_score
                if analysis.files[f].risk_score
                else 0.0,
                reverse=True,
            )
            analysis.most_impactful_files = sorted(
                analysis.files.keys(),
                key=lambda f: analysis.files[f].get_impact_score(),
                reverse=True,
            )
            
            analysis.total_files = len(analysis.files)
            analysis.total_lines = sum(
                ast_info.total_lines for ast_info in self.scanned_files.values()
            )
            
            return ToolResponse(
                success=True,
                message=f"Analyzed {len(analysis.files)} files",
                data={"analysis": analysis},
            )
            
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Analysis failed: {str(e)}",
                error=str(e),
            )
    
    def _analyze_file(self, file_path: str, ast_info: FileASTInfo) -> FileAnalysis:
        """Analyze a single file."""
        analysis = FileAnalysis(file_path=file_path)
        
        # Find dependencies (files this file imports)
        dependencies = self._find_file_dependencies(file_path, ast_info)
        analysis.dependencies = dependencies
        
        # Calculate complexity metrics
        analysis.complexity_metrics = self._calculate_complexity(ast_info)
        
        # Build function and class usage maps
        analysis.function_usage = self._map_function_usage(file_path, ast_info)
        analysis.class_usage = self._map_class_usage(file_path, ast_info)
        
        return analysis
    
    def _find_file_dependencies(
        self, file_path: str, ast_info: FileASTInfo
    ) -> List[FileDependency]:
        """Find all file dependencies for a given file."""
        dependencies = []
        source_path = Path(file_path)
        
        for import_node in ast_info.imports:
            # Try to resolve import to a file
            target_files = self._resolve_import_to_files(import_node, source_path)
            
            for target_file in target_files:
                if target_file != file_path:  # Skip self-references
                    dep = FileDependency(
                        source_file=file_path,
                        target_file=target_file,
                        dependency_type=DependencyType.IMPORT,
                        details={
                            "module": import_node.module,
                            "imported_items": import_node.imported_items,
                            "import_type": import_node.import_type,
                        },
                        strength=1.0 if import_node.import_type == "from_import" else 0.8,
                    )
                    dependencies.append(dep)
        
        return dependencies
    
    def _resolve_import_to_files(
        self, import_node: ImportNode, source_path: Path
    ) -> List[str]:
        """Resolve an import statement to actual file paths."""
        target_files = []
        
        # Get module path
        module = import_node.module
        if not module:
            return []
        
        # Handle relative imports
        if module.startswith("."):
            # Relative import - resolve relative to source file's directory
            parts = module.split(".")
            level = sum(1 for p in parts if not p)
            module_parts = [p for p in parts if p]
            
            base_dir = source_path.parent
            for _ in range(level):
                base_dir = base_dir.parent
            
            potential_path = base_dir / "/".join(module_parts)
            if potential_path.with_suffix(".py").exists():
                target_files.append(str(potential_path.with_suffix(".py")))
            elif potential_path.is_dir() and (potential_path / "__init__.py").exists():
                target_files.append(str(potential_path / "__init__.py"))
        else:
            # Absolute import - try to resolve
            module_parts = module.split(".")
            
            # Try to find in scanned files
            for scanned_path in self.scanned_files.keys():
                scanned_file = Path(scanned_path)
                
                # Check if this file matches the import
                # Convert file path to module path
                for root in self.root_paths:
                    try:
                        rel_path = scanned_file.relative_to(root)
                        file_module_parts = list(rel_path.with_suffix("").parts)
                        
                        # Remove __init__ if present
                        if file_module_parts and file_module_parts[-1] == "__init__":
                            file_module_parts = file_module_parts[:-1]
                        
                        # Check if module parts match
                        if file_module_parts == module_parts:
                            target_files.append(scanned_path)
                            break
                        
                        # Check if this is an __init__.py for the module
                        if (
                            scanned_file.name == "__init__.py"
                            and file_module_parts == module_parts
                        ):
                            target_files.append(scanned_path)
                            break
                    except ValueError:
                        continue
        
        return target_files
    
    def _calculate_complexity(self, ast_info: FileASTInfo) -> Dict[str, float]:
        """Calculate complexity metrics for a file."""
        metrics = {
            "total_lines": float(ast_info.total_lines),
            "code_lines": float(ast_info.code_lines),
            "num_functions": float(len(ast_info.functions)),
            "num_classes": float(len(ast_info.classes)),
            "num_imports": float(len(ast_info.imports)),
            "avg_function_length": 0.0,
            "max_function_length": 0.0,
        }
        
        if ast_info.functions:
            func_lengths = [
                f.line_end - f.line_start for f in ast_info.functions
            ]
            metrics["avg_function_length"] = sum(func_lengths) / len(func_lengths)
            metrics["max_function_length"] = max(func_lengths) if func_lengths else 0.0
        
        # Calculate nesting depth (simplified)
        metrics["max_nesting"] = 1.0  # Placeholder - would need AST traversal
        
        # Cyclomatic complexity approximation
        metrics["complexity_score"] = (
            metrics["num_functions"] * 2
            + metrics["num_classes"] * 3
            + metrics["num_imports"] * 0.5
        )
        
        return metrics
    
    def _map_function_usage(
        self, file_path: str, ast_info: FileASTInfo
    ) -> Dict[str, Set[str]]:
        """Map function names to files that might use them."""
        # This is a simplified version - in a full implementation,
        # we'd do cross-file call graph analysis
        usage_map = defaultdict(set)
        
        # For now, we'll build this when building dependency graphs
        # This is a placeholder structure
        for func in ast_info.functions:
            usage_map[func.name] = set()
        
        return dict(usage_map)
    
    def _map_class_usage(
        self, file_path: str, ast_info: FileASTInfo
    ) -> Dict[str, Set[str]]:
        """Map class names to files that might use them."""
        usage_map = defaultdict(set)
        
        for cls in ast_info.classes:
            usage_map[cls.name] = set()
        
        return dict(usage_map)
    
    def _build_dependency_graphs(self, analysis: CodebaseAnalysis):
        """Build forward and reverse dependency graphs."""
        for file_path, file_analysis in analysis.files.items():
            # Forward dependencies (what this file depends on)
            deps = set()
            for dep in file_analysis.dependencies:
                deps.add(dep.target_file)
            analysis.dependency_graph[file_path] = deps
            
            # Reverse dependencies (what depends on this file)
            if file_path not in analysis.reverse_dependency_graph:
                analysis.reverse_dependency_graph[file_path] = set()
            
            for dep in file_analysis.dependencies:
                target = dep.target_file
                if target not in analysis.reverse_dependency_graph:
                    analysis.reverse_dependency_graph[target] = set()
                analysis.reverse_dependency_graph[target].add(file_path)
        
        # Update dependents in file analyses
        for file_path, file_analysis in analysis.files.items():
            file_analysis.dependents = list(
                analysis.reverse_dependency_graph.get(file_path, set())
            )
    
    def _calculate_risk_scores(self, analysis: CodebaseAnalysis):
        """Calculate risk scores for all files."""
        from config.settings import settings
        
        for file_path, file_analysis in analysis.files.items():
            risk_score = self._calculate_file_risk(file_path, file_analysis, analysis)
            file_analysis.risk_score = risk_score
    
    def _calculate_file_risk(
        self, file_path: str, file_analysis: FileAnalysis, analysis: CodebaseAnalysis
    ) -> RiskScore:
        """Calculate risk score for a single file."""
        from config.settings import settings
        
        factors = {}
        
        # Complexity factor
        complexity = file_analysis.complexity_metrics.get("complexity_score", 0)
        factors["complexity"] = min(complexity / 50.0, 1.0)  # Normalize to 0-1
        
        # Dependency factor (more dependencies = higher risk)
        num_deps = len(file_analysis.dependencies)
        factors["dependencies"] = min(num_deps / 20.0, 1.0)
        
        # Dependents factor (more dependents = higher risk if changed)
        num_dependents = len(file_analysis.dependents)
        factors["dependents"] = min(num_dependents / 10.0, 1.0)
        
        # Size factor
        code_lines = file_analysis.complexity_metrics.get("code_lines", 0)
        factors["size"] = min(code_lines / 2000.0, 1.0)
        
        # Test coverage factor (placeholder - would need test analysis)
        factors["test_coverage"] = 0.5  # Assume medium risk
        
        # Calculate weighted overall score
        weights = settings.RISK_WEIGHTS
        overall_score = sum(
            factors.get(key, 0) * weights.get(key, 0) for key in weights
        )
        
        # Generate explanation
        explanation_parts = []
        if factors["complexity"] > 0.7:
            explanation_parts.append("High complexity")
        if factors["dependencies"] > 0.7:
            explanation_parts.append("Many dependencies")
        if factors["dependents"] > 0.7:
            explanation_parts.append("Many files depend on this")
        if factors["size"] > 0.7:
            explanation_parts.append("Large file size")
        
        explanation = "; ".join(explanation_parts) if explanation_parts else "Low to medium risk"
        
        return RiskScore(
            overall_score=overall_score,
            factors=factors,
            explanation=explanation,
        )
