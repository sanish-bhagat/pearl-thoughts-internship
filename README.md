# Code Analyzer Agent

A RAG-based LLM Agent built from scratch for analyzing codebases, understanding file relationships, and answering questions about code using both retrieved knowledge and static analysis.

## 🧠 Overview

This is a sophisticated LLM Agent (not just a chatbot) that:

- **Scans code files** using AST parsing to extract functions, classes, imports, and variables
- **Analyzes relationships** between files (imports, dependencies, calls)
- **Builds a knowledge base** from code analysis
- **Answers questions** using retrieved context, AST analysis, and LLM reasoning
- **Describe Files** provides a structured overview of a single file, including its functions, classes, imports, and variables.

## 🏗️ Architecture

```text
code-analyzer/
├── models/          # Core data models (AST nodes, analysis, agent state)
├── tools/           # Tools: FileScanner, CodeAnalyzer, RetrievalTool
├── knowledge_base/  # Vector store management (FAISS/Chroma)
├── agent/           # LangGraph agent orchestration
├── config/          # Configuration settings
└── main.py          # Entry point
└── sample_project/  # Example target project (calculator app)
```

## 🔧 Tech Stack

- **Python 3.9+**
- **LangGraph** - Agent orchestration
- **LangChain** - LLM integration
- **OpenRouter** - LLM API (supports multiple models)
- **AST module** - Static code analysis
- **FAISS/Chroma** - Vector store for RAG
- **sentence-transformers** - Embeddings

## 📦 Installation

### 1. Setup Conda Environment

```bash
conda activate code-analyzer
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup OpenRouter API Key

Get your API key from OpenRouter and configure it:

**Option 1: Using .env file (Recommended)**

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API key:
   ```env
   OPENROUTER_API_KEY=your-api-key-here
   ```

**Option 2: Environment Variable**

```bash
# On Linux/Mac:
export OPENROUTER_API_KEY="your-api-key-here"

# On Windows (PowerShell):
$env:OPENROUTER_API_KEY="your-api-key-here"

# On Windows (CMD):
set OPENROUTER_API_KEY=your-api-key-here
```

**Note:** Get your API key from https://openrouter.ai/keys  
**Note:** You can use free models or paid models. Default model is `deepseek/deepseek-chat` (configurable in `config/settings.py`)

## 🚀 Usage

### Basic Usage

```bash
python main.py --project /path/to/your/project --question "What is this codebase doing?"
```

### Interactive Mode

```bash
python main.py --project /path/to/your/project --interactive
```

### Example Questions

- "What is this codebase doing?"
- "Which file is the most risky and why?"
- "How are these two files related?"
- "Which function impacts the most files?"
- "What happens if I modify this function?"
- "Summarize the architecture of this codebase"
- "Describe the file `sample_project/calculator.py`"
- "What classes and functions are defined in `path/to/file.py`?"

## 🔍 How It Works

### 1. File Scanner Tool

Recursively scans the project directory and uses AST parsing to extract:
- File paths
- Functions (with parameters, return types, docstrings)
- Classes (with methods, bases, decorators)
- Imports (absolute and relative)
- Global variables

### 2. Code Analysis Tool

Analyzes the scanned AST data to compute:
- **Dependency graph** - Which files depend on which
- **Cross-file usage** - Functions/classes used across files
- **Complexity metrics** - Lines, nesting, number of imports
- **Risk scores** - Heuristic-based risk assessment per file

### 3. Knowledge Base (RAG Layer)

Converts AST summaries, file-level analysis, and dependency relationships into embeddings and stores them in a vector database for semantic retrieval.

### 4. LLM Agent (LangGraph)

The agent uses LangGraph to orchestrate:
- **Decision making** - When to scan, analyze, or retrieve
- **Tool usage** - Calls tools based on query needs
- **Reasoning** - Combines LLM knowledge, retrieved context, and code analysis
It binds the following tools to the model:
- `scan_files` – scan a project and populate `FileASTInfo` objects
- `analyze_files` – build dependency graph, complexity, and risk scores
- `retrieve_context` – perform semantic search over the knowledge base
- `describe_file` – provide a structured overview of a single file

### 5. File Description Tool

Provides structured overviews of individual files using AST data and analysis:
- Summarizes classes, functions, and their line ranges
- Shows imports, global variables, and basic metrics (lines of code)
- Includes dependency and risk information when available

You can trigger it with questions like:
- "Describe the file `sample_project/calculator.py`"
- "What classes and functions are defined in `path/to/file.py`?"

## 🛠 Tools Summary

This section summarizes the main tools and components used by the agent.

### FileScanner (`tools/file_scanner.py`)

- Recursively walks the project root and filters Python files (respecting `EXCLUDE_PATTERNS` and size limits).
- Parses each file into an AST and produces a `FileASTInfo`:
  - Functions (`FunctionNode`) with parameters, return annotations, docstrings, and line ranges
  - Classes (`ClassNode`) with bases, decorators, methods, and line ranges
  - Imports (`ImportNode`) and global variables (`VariableNode`)
  - Total lines and code lines (excluding comments/blank lines)

### CodeAnalyzer (`tools/code_analyzer.py`)

- Consumes the `{file_path -> FileASTInfo}` mapping and builds a `CodebaseAnalysis`:
  - Per-file `FileAnalysis` (dependencies, dependents, complexity metrics, risk scores)
  - Global `dependency_graph` and `reverse_dependency_graph`
  - Ranked lists of `most_risky_files` and `most_impactful_files`
- Risk scores combine factors such as complexity, dependency fan-in/fan-out, and file size.

### RetrievalTool (`tools/retrieval_tool.py`) and VectorStore

- `RetrievalTool` converts AST and analysis into text documents and indexes them:
  - File-level summaries (functions, classes, imports, errors)
  - Function-level and class-level documents
  - Dependency documents (who depends on whom, risk context)
- Uses `knowledge_base/VectorStore` to:
  - Initialize FAISS or Chroma (as configured by `VECTOR_STORE_TYPE`)
  - Add texts with metadata and perform similarity search

### Agent Orchestrator (`agent/orchestrator.py`)

- Provides a high-level Python API around the graph:
  - `AgentOrchestrator(project_path).answer_question(question)`
- Manages conversation history via `MemorySaver` (optional).
- Hides LangGraph specifics from CLI users and other integrations.

## ⚙️ Configuration

Configuration is managed in `config/settings.py`. Key settings:

- **OPENROUTER_API_KEY** - OpenRouter API key (required, get from https://openrouter.ai/keys)
- **OPENROUTER_BASE_URL** - OpenRouter API endpoint (default: `https://openrouter.ai/api/v1`)
- **LLM_MODEL** - Model to use (default: `deepseek/deepseek-chat`)
- **VECTOR_STORE_TYPE** - `faiss` or `chroma`
- **EMBEDDING_MODEL** - Sentence transformer model
- **EXCLUDE_PATTERNS** - Files/directories to exclude from analysis

You can configure settings using a `.env` file or environment variables:

**Using .env file (recommended):**

Create a `.env` file in the project root:
```env
OPENROUTER_API_KEY=your-api-key-here
LLM_MODEL=deepseek/deepseek-chat
VECTOR_STORE_TYPE=faiss
```

**Using environment variables:**

```bash
export OPENROUTER_API_KEY=your-api-key-here
export LLM_MODEL=deepseek/deepseek-chat
export VECTOR_STORE_TYPE=faiss
```

The `.env` file is automatically loaded by the application.

## 📊 Example Workflow

1. **User asks**: "What is this codebase doing?"

2. **Agent decides**: Needs to scan and analyze files first

3. **Agent calls**: `scan_files(project_path)`
   - Scans all Python files
   - Extracts AST information

4. **Agent calls**: `analyze_files()`
   - Builds dependency graph
   - Calculates complexity and risk scores

5. **Agent calls**: `retrieve_context(query)`
   - Builds knowledge base from analysis
   - Retrieves relevant context

6. **Agent reasons**: Combines retrieved context, AST facts, and LLM knowledge

7. **Agent responds**: Provides grounded, explainable answer

## 🎯 Key Features

✅ **AST-based static analysis** - No regex, proper Python parsing  
✅ **Dependency graph construction** - Understands file relationships  
✅ **Risk scoring** - Identifies risky files based on heuristics  
✅ **Semantic retrieval** - RAG-based context retrieval  
✅ **Tool-based reasoning** - Agent decides when to use which tools  
✅ **Explainable answers** - Based on AST facts, not hallucinations  

## 🔧 Development

The codebase is modular and extensible:

- **Models** (`models/`) - Clear data models for all components
- **Tools** (`tools/`) - Independent, testable tools
- **Agent** (`agent/`) - LangGraph orchestration with clear state transitions
- **Knowledge Base** (`knowledge_base/`) - Vector store abstraction

## 📝 Notes

- The agent requires an OpenRouter API key (get from https://openrouter.ai/keys)
- You can use free models or paid models via OpenRouter
- Large codebases may take time to analyze initially
- The vector store is persisted in `./vector_db/`
- Python files over 10MB are excluded by default (configurable)

## 🤝 Contributing

This is a production-grade implementation built from scratch with:
- Clean separation of concerns
- Modular, extensible design
- Clear data models
- Proper error handling
- Comprehensive documentation
