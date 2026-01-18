"""Agent orchestrator for executing queries."""

from typing import Optional, Dict, Any
from pathlib import Path

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver

from models.agent_models import AgentState
from agent.graph import create_agent_graph, initialize_tools, GraphState
from config.settings import settings


class AgentOrchestrator:
    """Orchestrates the code analyzer agent."""
    
    def __init__(self, project_path: str, enable_history: bool = True):
        """
        Initialize the orchestrator.
        
        Args:
            project_path: Path to the project root to analyze
            enable_history: Whether to enable conversation history (default: True)
        """
        self.project_path = Path(project_path).resolve()
        self.memory = MemorySaver() if enable_history else None
        
        # Create graph with checkpointer for history
        self.graph = create_agent_graph(checkpointer=self.memory)
        
        # Initialize tools
        initialize_tools(str(self.project_path))
    
    def answer_question(self, question: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Answer a question about the codebase.
        
        Args:
            question: User's question
            config: Optional LangGraph config
            
        Returns:
            Dictionary with answer and metadata
        """
        if config is None:
            config = {
                "configurable": {
                    "thread_id": "default",
                }
            }
        
        # If memory is enabled, load previous state or create new
        if self.memory:
            # With checkpointer, we only need to add the new message
            # The graph will load previous conversation history automatically
            initial_state = {
                "messages": [HumanMessage(content=question)],
            }
        else:
            # Without memory, create fresh state each time
            initial_state: GraphState = {
                "messages": [HumanMessage(content=question)],
                "scanned_files": {},
                "codebase_analysis": {},
                "analysis_complete": False,
                "retrieved_context": [],
                "knowledge_base_path": "",
                "reasoning_steps": [],
                "tool_calls": [],
                "answer": "",
                "confidence": 0.0,
            }
        
        try:
            # Invoke the graph (with memory, previous messages are automatically loaded)
            final_state = self.graph.invoke(
                initial_state,
                config=config,
            )
            
            # Extract answer from messages
            messages = final_state.get("messages", [])
            answer = ""
            
            # Find the last AI message
            for message in reversed(messages):
                if isinstance(message, AIMessage):
                    answer = message.content
                    break
            
            if not answer:
                answer = "I was unable to generate an answer."
            
            return {
                "answer": answer,
                "messages": [
                    {
                        "role": msg.__class__.__name__.replace("Message", "").lower(),
                        "content": msg.content if hasattr(msg, "content") else str(msg),
                    }
                    for msg in messages
                ],
                "tool_calls": final_state.get("tool_calls", []),
                "reasoning_steps": final_state.get("reasoning_steps", []),
                "retrieved_context": final_state.get("retrieved_context", []),
            }
            
        except Exception as e:
            return {
                "answer": f"Error processing question: {str(e)}",
                "error": str(e),
                "messages": [],
            }
    
    def is_codebase_analyzed(self) -> bool:
        """Check if the codebase has been analyzed."""
        # This would check if vector store exists and has content
        # For now, return False to always trigger analysis
        from knowledge_base.vector_store import VectorStore
        
        store = VectorStore()
        return store.is_initialized()
