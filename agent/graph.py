"""LangGraph Agent for code analysis"""

from typing import Any, Dict, Optional, List, Annotated, TypedDict
import operator
from langgraph.graph import StateGraph, END
from models import AnalysisResult
from tools import FileScanner, CodeAnalyzer
from knowledge_base import KnowledgeBase
from agent.llm import OllamaClient

class GraphState(TypedDict):
    """State for the LangGraph workflow"""
    question: str
    analysis_result: Optional[AnalysisResult]
    context: Annotated[List[str], operator.add]
    answer: str
    reasoning: Annotated[List[str], operator.add]
    needs_analysis: bool
    root_path: str

class CodeAnalysisAgent:
    """Code analysis agent with LangGraph orchestration"""
    
    def __init__(self, use_embeddings: bool = False):
        """Initialize agent"""
        self.scanner = FileScanner()
        self.analyzer = CodeAnalyzer()
        self.knowledge_base = KnowledgeBase(use_embeddings=use_embeddings)
        self.llm = OllamaClient()
        self.analysis_result: Optional[AnalysisResult] = None
        self.app = self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("check_analysis", self._check_analysis)
        workflow.add_node("analyze_code", self._analyze_code)
        workflow.add_node("retrieve_context", self._retrieve_context)
        workflow.add_node("generate_answer", self._generate_answer)
        
        # Define edges
        workflow.set_entry_point("check_analysis")
        
        workflow.add_conditional_edges(
            "check_analysis",
            lambda x: "analyze_code" if x.get("needs_analysis") else "retrieve_context"
        )
        
        workflow.add_edge("analyze_code", "retrieve_context")
        workflow.add_edge("retrieve_context", "generate_answer")
        workflow.add_edge("generate_answer", END)
        
        return workflow.compile()

    def _check_analysis(self, state: GraphState) -> Dict[str, Any]:
        """Check if analysis is needed"""
        reasoning = []
        needs_analysis = False
        
        if not self.analysis_result:
            reasoning.append("No analysis found. Scheduling full scan.")
            needs_analysis = True
        else:
            reasoning.append("Using existing analysis result.")
            
        return {
            "needs_analysis": needs_analysis,
            "reasoning": reasoning,
            "analysis_result": self.analysis_result
        }

    def _analyze_code(self, state: GraphState) -> Dict[str, Any]:
        """Run code analysis"""
        root_path = state.get("root_path", "./code_samples")
        
        # Scan
        files = self.scanner.scan_directory(root_path)
        
        # Analyze
        analysis_result = self.analyzer.analyze(files)
        analysis_result.root_path = root_path
        
        # Update instance state
        self.analysis_result = analysis_result
        
        # Build KB
        self.knowledge_base.build_from_analysis(analysis_result)
        
        return {
            "analysis_result": analysis_result,
            "reasoning": [f"Analyzed {len(files)} files and built knowledge base."],
            "needs_analysis": False
        }

    def _retrieve_context(self, state: GraphState) -> Dict[str, Any]:
        """Retrieve relevant context"""
        question = state["question"]
        docs = self.knowledge_base.retrieve(question, top_k=5)
        
        context_strs = [doc.content for doc in docs]
        
        return {
            "context": context_strs,
            "reasoning": [f"Retrieved {len(docs)} documents for context."]
        }

    def _generate_answer(self, state: GraphState) -> Dict[str, Any]:
        """Generate answer using LLM"""
        question = state["question"]
        context = state["context"]
        
        # Fallback if no context
        if not context:
            return {
                "answer": "I couldn't find relevant information in the codebase to answer your question.",
                "reasoning": ["No context found."]
            }
            
        # Prepare prompt
        context_text = "\n\n".join(context)
        prompt = f"""You are a code analysis expert. Answer the question based ONLY on the provided context.
        
Context:
{context_text}

Question: {question}

Answer:"""
        
        response = self.llm.generate(prompt)
        
        if not response:
             response = "I'm unable to generate a response at the moment. (LLM unavailable)"
             
        return {
            "answer": response
        }

    def query(self, question: str, root_path: str = "./code_samples") -> Dict[str, Any]:
        """Process a query through the agent"""
        
        initial_state: GraphState = {
            "question": question,
            "root_path": root_path,
            "analysis_result": self.analysis_result,
            "context": [],
            "answer": "",
            "reasoning": [],
            "needs_analysis": False
        }
        
        result = self.app.invoke(initial_state)
        
        return {
            "question": question,
            "answer": result["answer"],
            "reasoning": result["reasoning"]
        }
