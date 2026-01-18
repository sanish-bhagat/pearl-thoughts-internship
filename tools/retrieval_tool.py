"""Retrieval tool for RAG-based context retrieval."""

from typing import List, Dict, Any, Optional
from pathlib import Path

from models.agent_models import ToolResponse
from knowledge_base.vector_store import VectorStore


class RetrievalTool:
    """Tool for retrieving relevant context from the knowledge base."""
    
    def __init__(self, vector_store: Optional[VectorStore] = None):
        """
        Initialize the retrieval tool.
        
        Args:
            vector_store: VectorStore instance (creates new if not provided)
        """
        self.vector_store = vector_store or VectorStore()
    
    def retrieve(self, query: str, top_k: int = 5) -> ToolResponse:
        """
        Retrieve relevant context from the knowledge base.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            ToolResponse with retrieved context
        """
        if not self.vector_store.is_initialized():
            return ToolResponse(
                success=False,
                message="Knowledge base is not initialized. Please scan and analyze files first.",
                error="NotInitialized",
            )
        
        try:
            results = self.vector_store.search(query, top_k=top_k)
            
            context = []
            for result in results:
                context.append({
                    "content": result.get("content", ""),
                    "metadata": result.get("metadata", {}),
                    "score": result.get("score", 0.0),
                })
            
            return ToolResponse(
                success=True,
                message=f"Retrieved {len(context)} relevant contexts",
                data={
                    "context": context,
                    "query": query,
                    "top_k": top_k,
                },
            )
            
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Retrieval failed: {str(e)}",
                error=str(e),
            )
    
    def build_knowledge_base(
        self, scanned_files: Dict[str, Any], codebase_analysis: Any
    ) -> ToolResponse:
        """
        Build or update the knowledge base from scanned files and analysis.
        
        Args:
            scanned_files: Dictionary of file paths to FileASTInfo
            codebase_analysis: CodebaseAnalysis object
            
        Returns:
            ToolResponse indicating success/failure
        """
        try:
            documents = []
            
            # Add file-level summaries
            for file_path, ast_info in scanned_files.items():
                doc_content = self._file_to_document(file_path, ast_info)
                documents.append({
                    "content": doc_content,
                    "metadata": {
                        "type": "file_summary",
                        "file_path": file_path,
                        "language": ast_info.language,
                    },
                })
                
                # Add function-level details
                for func in ast_info.functions:
                    func_doc = self._function_to_document(file_path, func)
                    documents.append({
                        "content": func_doc,
                        "metadata": {
                            "type": "function",
                            "file_path": file_path,
                            "function_name": func.name,
                            "line_start": func.line_start,
                            "line_end": func.line_end,
                        },
                    })
                
                # Add class-level details
                for cls in ast_info.classes:
                    cls_doc = self._class_to_document(file_path, cls)
                    documents.append({
                        "content": cls_doc,
                        "metadata": {
                            "type": "class",
                            "file_path": file_path,
                            "class_name": cls.name,
                            "line_start": cls.line_start,
                            "line_end": cls.line_end,
                        },
                    })
            
            # Add dependency information
            if codebase_analysis:
                for file_path, file_analysis in codebase_analysis.files.items():
                    deps_doc = self._dependencies_to_document(file_path, file_analysis)
                    documents.append({
                        "content": deps_doc,
                        "metadata": {
                            "type": "dependencies",
                            "file_path": file_path,
                        },
                    })
            
            # Add documents to vector store
            self.vector_store.add_documents(documents)
            
            return ToolResponse(
                success=True,
                message=f"Built knowledge base with {len(documents)} documents",
                data={"num_documents": len(documents)},
            )
            
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Failed to build knowledge base: {str(e)}",
                error=str(e),
            )
    
    def _file_to_document(self, file_path: str, ast_info: Any) -> str:
        """Convert file AST info to document text."""
        parts = [
            f"File: {file_path}",
            f"Language: {ast_info.language}",
            f"Total lines: {ast_info.total_lines}",
            f"Code lines: {ast_info.code_lines}",
        ]
        
        if ast_info.functions:
            func_names = [f.name for f in ast_info.functions]
            parts.append(f"Functions: {', '.join(func_names)}")
        
        if ast_info.classes:
            class_names = [c.name for c in ast_info.classes]
            parts.append(f"Classes: {', '.join(class_names)}")
        
        if ast_info.imports:
            imports_list = [i.module for i in ast_info.imports[:10]]  # Limit imports
            parts.append(f"Imports: {', '.join(imports_list)}")
        
        if ast_info.parse_error:
            parts.append(f"Parse error: {ast_info.parse_error}")
        
        return "\n".join(parts)
    
    def _function_to_document(self, file_path: str, func: Any) -> str:
        """Convert function info to document text."""
        parts = [
            f"Function: {func.name}",
            f"File: {file_path}",
            f"Lines: {func.line_start}-{func.line_end}",
        ]
        
        if func.parameters:
            parts.append(f"Parameters: {', '.join(func.parameters)}")
        
        if func.return_annotation:
            parts.append(f"Returns: {func.return_annotation}")
        
        if func.docstring:
            parts.append(f"Docstring: {func.docstring}")
        
        if func.is_method:
            parts.append(f"Method of class: {func.parent_class}")
        
        if func.is_async:
            parts.append("Type: async function")
        
        return "\n".join(parts)
    
    def _class_to_document(self, file_path: str, cls: Any) -> str:
        """Convert class info to document text."""
        parts = [
            f"Class: {cls.name}",
            f"File: {file_path}",
            f"Lines: {cls.line_start}-{cls.line_end}",
        ]
        
        if cls.bases:
            parts.append(f"Inherits from: {', '.join(cls.bases)}")
        
        if cls.methods:
            method_names = [m.name for m in cls.methods]
            parts.append(f"Methods: {', '.join(method_names)}")
        
        if cls.docstring:
            parts.append(f"Docstring: {cls.docstring}")
        
        return "\n".join(parts)
    
    def _dependencies_to_document(self, file_path: str, file_analysis: Any) -> str:
        """Convert dependency info to document text."""
        parts = [
            f"Dependencies for: {file_path}",
        ]
        
        if file_analysis.dependencies:
            dep_files = [d.target_file for d in file_analysis.dependencies]
            parts.append(f"Depends on: {', '.join(dep_files[:10])}")
        
        if file_analysis.dependents:
            parts.append(f"Dependents: {', '.join(file_analysis.dependents[:10])}")
        
        if file_analysis.risk_score:
            parts.append(f"Risk score: {file_analysis.risk_score.overall_score:.2f}")
            parts.append(f"Risk explanation: {file_analysis.risk_score.explanation}")
        
        return "\n".join(parts)
