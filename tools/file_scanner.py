"""File scanner tool using AST parsing."""

import ast
import os
from pathlib import Path
from typing import List, Dict, Optional
import fnmatch

from models.ast_models import (
    FileASTInfo,
    FunctionNode,
    ClassNode,
    ImportNode,
    VariableNode,
)
from models.agent_models import ToolResponse
from config.settings import settings


class FileScanner:
    """Scans codebase files and extracts AST information."""
    
    def __init__(self, root_path: str, exclude_patterns: Optional[List[str]] = None):
        """
        Initialize the file scanner.
        
        Args:
            root_path: Root directory to scan
            exclude_patterns: Patterns to exclude (defaults to settings.EXCLUDE_PATTERNS)
        """
        self.root_path = Path(root_path).resolve()
        self.exclude_patterns = exclude_patterns or settings.EXCLUDE_PATTERNS
        self.max_file_size_mb = settings.MAX_FILE_SIZE_MB
    
    def should_exclude(self, file_path: Path) -> bool:
        """Check if a file should be excluded based on patterns."""
        path_str = str(file_path)
        # Normalize path separators for Windows
        path_str = path_str.replace("\\", "/")
        
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(
                file_path.name, pattern
            ):
                return True
        return False
    
    def scan_directory(self) -> ToolResponse:
        """
        Recursively scan the directory for Python files.
        
        Returns:
            ToolResponse with scanned files data
        """
        if not self.root_path.exists():
            return ToolResponse(
                success=False,
                message=f"Root path does not exist: {self.root_path}",
                error="PathNotFound",
            )
        
        if not self.root_path.is_dir():
            return ToolResponse(
                success=False,
                message=f"Root path is not a directory: {self.root_path}",
                error="NotADirectory",
            )
        
        python_files = []
        
        for root, dirs, files in os.walk(self.root_path):
            # Filter out excluded directories
            dirs[:] = [
                d
                for d in dirs
                if not self.should_exclude(Path(root) / d)
            ]
            
            for file in files:
                if not file.endswith(".py"):
                    continue
                
                file_path = Path(root) / file
                
                # Check if file should be excluded
                if self.should_exclude(file_path):
                    continue
                
                # Check file size
                try:
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    if size_mb > self.max_file_size_mb:
                        continue
                except OSError:
                    continue
                
                python_files.append(file_path)
        
        return ToolResponse(
            success=True,
            message=f"Found {len(python_files)} Python files",
            data={"files": [str(f) for f in python_files]},
        )
    
    def parse_file(self, file_path: Path) -> FileASTInfo:
        """
        Parse a single Python file and extract AST information.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            FileASTInfo object with parsed AST data
        """
        ast_info = FileASTInfo(file_path=str(file_path))
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Count lines
            lines = content.splitlines()
            ast_info.total_lines = len(lines)
            ast_info.code_lines = sum(
                1 for line in lines if line.strip() and not line.strip().startswith("#")
            )
            
            # Parse AST
            tree = ast.parse(content, filename=str(file_path))
            
            # Extract information
            ast_info.imports = self._extract_imports(tree)
            ast_info.classes = self._extract_classes(tree)
            ast_info.functions = self._extract_functions(tree)
            ast_info.variables = self._extract_variables(tree)
            
        except SyntaxError as e:
            ast_info.parse_error = f"SyntaxError: {str(e)}"
        except UnicodeDecodeError as e:
            ast_info.parse_error = f"UnicodeDecodeError: {str(e)}"
        except Exception as e:
            ast_info.parse_error = f"Error: {str(e)}"
        
        return ast_info
    
    def _extract_imports(self, tree: ast.AST) -> List[ImportNode]:
        """Extract all import statements from AST."""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        ImportNode(
                            module=alias.name,
                            alias=alias.asname,
                            import_type="import",
                        )
                    )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imported_items = [alias.name for alias in node.names]
                
                imports.append(
                    ImportNode(
                        module=module,
                        imported_items=imported_items,
                        import_type="from_import_all" if "*" in imported_items else "from_import",
                    )
                )
        
        return imports
    
    def _extract_functions(self, tree: ast.AST) -> List[FunctionNode]:
        """Extract all function definitions from AST."""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func = self._parse_function(node, is_method=False)
                functions.append(func)
            elif isinstance(node, ast.AsyncFunctionDef):
                func = self._parse_function(node, is_method=False, is_async=True)
                functions.append(func)
        
        return functions
    
    def _extract_classes(self, tree: ast.AST) -> List[ClassNode]:
        """Extract all class definitions from AST."""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_node = ClassNode(
                    name=node.name,
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    bases=[self._get_name(base) for base in node.bases],
                    decorators=[self._get_name(dec) for dec in node.decorator_list],
                    docstring=ast.get_docstring(node),
                )
                
                # Extract methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method = self._parse_function(item, is_method=True, parent_class=node.name)
                        class_node.methods.append(method)
                    elif isinstance(item, ast.AsyncFunctionDef):
                        method = self._parse_function(
                            item, is_method=True, parent_class=node.name, is_async=True
                        )
                        class_node.methods.append(method)
                
                classes.append(class_node)
        
        return classes
    
    def _parse_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        is_method: bool = False,
        parent_class: Optional[str] = None,
        is_async: bool = False,
    ) -> FunctionNode:
        """Parse a function or method node."""
        # Extract parameters
        params = []
        for arg in node.args.args:
            param = arg.arg
            if arg.annotation:
                param += f": {ast.unparse(arg.annotation)}"
            params.append(param)
        
        # Extract return annotation
        return_annotation = None
        if node.returns:
            return_annotation = ast.unparse(node.returns)
        
        return FunctionNode(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            parameters=params,
            return_annotation=return_annotation,
            decorators=[self._get_name(dec) for dec in node.decorator_list],
            docstring=ast.get_docstring(node),
            is_async=is_async,
            is_method=is_method,
            parent_class=parent_class,
        )
    
    def _extract_variables(self, tree: ast.AST) -> List[VariableNode]:
        """Extract global variables and constants from AST."""
        variables = []
        
        # Only extract module-level assignments
        for node in ast.walk(tree):
            if isinstance(node, ast.Module):
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                var_name = target.id
                                is_constant = var_name.isupper() and "_" in var_name
                                
                                annotation = None
                                value = None
                                
                                if item.value:
                                    try:
                                        value = ast.unparse(item.value)
                                    except:
                                        value = None
                                
                                variables.append(
                                    VariableNode(
                                        name=var_name,
                                        line=item.lineno,
                                        annotation=annotation,
                                        value=value,
                                        is_constant=is_constant,
                                    )
                                )
                    elif isinstance(item, ast.AnnAssign):
                        # Annotated assignment (e.g., x: int = 5)
                        if isinstance(item.target, ast.Name):
                            var_name = item.target.id
                            annotation = (
                                ast.unparse(item.annotation) if item.annotation else None
                            )
                            value = ast.unparse(item.value) if item.value else None
                            
                            variables.append(
                                VariableNode(
                                    name=var_name,
                                    line=item.lineno,
                                    annotation=annotation,
                                    value=value,
                                    is_constant=var_name.isupper() and "_" in var_name,
                                )
                            )
        
        return variables
    
    def _get_name(self, node: ast.AST) -> str:
        """Get a string representation of an AST node."""
        try:
            if isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Attribute):
                return ast.unparse(node)
            elif isinstance(node, ast.Call):
                return ast.unparse(node.func)
            else:
                return ast.unparse(node)
        except:
            return str(type(node).__name__)
    
    def scan_all_files(self) -> Dict[str, FileASTInfo]:
        """
        Scan all Python files in the directory and parse them.
        
        Returns:
            Dictionary mapping file paths to FileASTInfo objects
        """
        scan_result = self.scan_directory()
        
        if not scan_result.success:
            return {}
        
        file_paths = scan_result.data.get("files", [])
        scanned_files = {}
        
        for file_path_str in file_paths:
            file_path = Path(file_path_str)
            ast_info = self.parse_file(file_path)
            scanned_files[str(file_path)] = ast_info
        
        return scanned_files
