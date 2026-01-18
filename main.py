"""Main entry point for the code analysis agent"""

from agent import CodeAnalysisAgent
from models import RiskLevel
import json


def print_separator(title: str = ""):
    """Print a separator line"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")
    else:
        print(f"\n{'-'*60}\n")


def print_result(result: dict):
    """Pretty print agent result"""
    print(f"Question: {result['question']}")
    print(f"\nReasoning Steps:")
    for i, step in enumerate(result['reasoning'], 1):
        print(f"  {i}. {step}")
    
    print(f"\nAnswer:")
    print(result['answer'])
    
    if result.get('analysis_summary'):
        print(f"\nAnalysis Summary:")
        summary = result['analysis_summary']
        print(f"  - Files analyzed: {summary['files']}")
        print(f"  - Functions found: {summary['functions']}")
        print(f"  - Classes found: {summary['classes']}")


def main():
    """Run example queries against code_samples"""
    
    print_separator("CODE ANALYSIS AGENT - LangGraph Based")
    print("Initializing agent...")
    
    agent = CodeAnalysisAgent(use_embeddings=False)
    
    print(f"[OK] Agent initialized")
    print(f"[OK] LLM Status: {'Connected' if agent.llm.is_connected else 'Not Connected (responses will use retrieved context)'}")
    
    # Example queries demonstrating agent capabilities
    queries = [
        # Query 1: Explain file
        "What is this database_utils.py file doing?",
        
        # Query 2: Relationships
        "How are database_utils and user_management related?",
        
        # Query 3: Risk assessment
        "Is it safe to modify the connect_database function?",
        
        # Query 4: Complex analysis
        "Which file is most risky to modify and why?",
        
        # Query 5: Architecture understanding
        "What functions impact the most files?",
    ]
    
    print_separator("EXAMPLE QUERIES")
    
    for i, query in enumerate(queries, 1):
        print_separator(f"Query {i}/{len(queries)}")
        
        result = agent.query(query, root_path="./code_samples")
        print_result(result)
        print_separator()


def interactive_mode():
    """Run agent in interactive mode"""
    
    print_separator("CODE ANALYSIS AGENT - Interactive Mode")
    print("Initializing agent...")
    
    agent = CodeAnalysisAgent(use_embeddings=False)
    
    print(f"[OK] Agent initialized")
    print(f"[OK] LLM Status: {'Connected' if agent.llm.is_connected else 'Not Connected'}")
    print("\nCommands:")
    print("  'exit' or 'quit' - Exit the agent")
    print("  'rescan [path]' - Rescan a directory")
    print("  'status' - Show analysis status")
    print("  Any other input - Ask a question about the code\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting agent. Goodbye!")
                break
            
            if user_input.lower().startswith('rescan'):
                parts = user_input.split()
                path = parts[1] if len(parts) > 1 else "./code_samples"
                print(f"Rescanning {path}...")
                agent.analysis_result = None
                agent.knowledge_base.documents.clear()
                result = agent.query("", root_path=path)
                print("Rescan complete!")
                continue
            
            if user_input.lower() == 'status':
                if agent.analysis_result:
                    print(f"Analysis Status: READY")
                    print(f"  Files: {agent.analysis_result.total_files}")
                    print(f"  Functions: {agent.analysis_result.total_functions}")
                    print(f"  Classes: {agent.analysis_result.total_classes}")
                    print(f"  KB Documents: {len(agent.knowledge_base.documents)}")
                else:
                    print("Analysis Status: NOT INITIALIZED")
                continue
            
            # Process query
            result = agent.query(user_input)
            print(f"\nAgent: {result['answer']}\n")
        
        except KeyboardInterrupt:
            print("\nInterrupted. Exiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        main()
