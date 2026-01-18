"""Agent state and tool response models."""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from .ast_models import FileASTInfo
from .analysis_models import CodebaseAnalysis


@dataclass
class ToolResponse:
    """Response from a tool execution."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class AgentState:
    """State maintained by the LangGraph agent."""
    # User input
    question: str = ""
    
    # Analysis state
    scanned_files: Dict[str, FileASTInfo] = field(default_factory=dict)  # file_path -> FileASTInfo
    codebase_analysis: Optional[CodebaseAnalysis] = None
    analysis_complete: bool = False
    
    # RAG state
    retrieved_context: List[Dict[str, Any]] = field(default_factory=list)  # Retrieved chunks
    knowledge_base_path: Optional[str] = None
    
    # Agent reasoning
    messages: List[Dict[str, str]] = field(default_factory=list)  # LLM conversation history
    reasoning_steps: List[str] = field(default_factory=list)  # Agent's reasoning process
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)  # History of tool calls
    
    # Final answer
    answer: Optional[str] = None
    confidence: float = 0.0  # 0.0 to 1.0
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation history."""
        self.messages.append({"role": role, "content": content})
    
    def add_reasoning(self, step: str):
        """Add a reasoning step."""
        self.reasoning_steps.append(step)
    
    def add_tool_call(self, tool_name: str, arguments: Dict[str, Any], result: Any):
        """Record a tool call."""
        self.tool_calls.append({
            "tool": tool_name,
            "arguments": arguments,
            "result": result,
        })
