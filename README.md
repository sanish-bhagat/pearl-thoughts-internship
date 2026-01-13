# Code Analyzer

A simple Python code analyzer that parses Python files using AST (Abstract Syntax Tree) to provide insights into the code structure, relationships, and risks.

## Features

- Counts total functions and classes in a Python file.
- Identifies call relationships between functions (who calls what).
- Assesses risk for each function based on incoming dependencies (number of functions that call it).
- Highlights the most risky function with its description (docstring) and lists callers at risk if changed, including their descriptions.

## Structure

The project is organized into three main files, each handling a specific responsibility:

- `parser.py`: Handles parsing Python files into AST and collecting functions, classes, and function calls.
- `analyzer.py`: Builds the call graph, calculates risks, and generates the analysis report.
- `main.py`: Orchestrates the analysis and prints the report.

## Requirements

- Python 3.x
- Standard library modules: `ast`, `pathlib`

No external dependencies required.

## Usage

1. Place the Python file you want to analyze in the project directory (e.g., `sample.py`).

2. Run the analyzer:

   ```
   python main.py
   ```

   By default, it analyzes `some_file.py`. To analyze a different file, modify the `file_path` variable in `main.py`.

## Example

Given a file `sample.py` with the following content:

```python
def add(a, b):
    """
    Adds Two Numbers
    """
    return a + b

def add_3(a, b, c):
    return add(a, b) + c

def mul(a, b):
    add(a, b)
    return a * b
```

Running `python main.py` produces:

```
Code Analysis Summary
==============================
Total Functions: 3
  - add
  - add_3
  - mul

Total Classes: 0

Call Relationships (Who calls what):
  add calls nothing
  add_3 calls: add
  mul calls: add

Risk Assessment (based on incoming dependencies):
  add: Risk 2 (called by 2 functions)
  add_3: Risk 0 (called by 0 functions)
  mul: Risk 0 (called by 0 functions)

Most Risky Function: add
Description: Adds Two Numbers
Callers at risk if changed: add_3, mul
  add_3 description:
  mul description:
```

## How It Works

- **Parsing**: Uses Python's `ast` module to parse the code into an AST.
- **Collection**: Collects function definitions, class definitions, and function calls.
- **Analysis**: Builds a call graph and calculates risk based on how many functions depend on each function.
- **Reporting**: Generates a plain text summary with all the insights.

## Contributing

Feel free to contribute by improving the analyzer, adding more features, or fixing bugs.

## License

This project is open-source. Use it as you wish.