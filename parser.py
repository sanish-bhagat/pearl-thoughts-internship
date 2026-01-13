import ast
from pathlib import Path

def parse_file(file_path):
    """
    Parses the given Python file into an AST tree.
    Args:
        file_path (str or Path): Path to the Python file.
    Returns:
        ast.Module: The parsed AST tree.
    Raises:
        FileNotFoundError: If the file does not exist.
        SyntaxError: If the file has syntax errors.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File {file_path} not found.")
    with open(path, 'r') as f:
        code = f.read()
    try:
        tree = ast.parse(code, filename=str(path))
        return tree
    except SyntaxError as e:
        raise SyntaxError(f"Syntax error in {file_path}: {e}")

def collect_functions_and_classes(tree):
    """
    Walks the AST tree to collect all function and class definitions with their docstrings.
    Args:
        tree (ast.Module): The AST tree.
    Returns:
        dict: {'functions': list of {'name':, 'doc':}, 'classes': list of class names}
    """
    functions = []
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            doc = ast.get_docstring(node) or ""
            functions.append({'name': node.name, 'doc': doc})
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
    return {'functions': functions, 'classes': classes}

class CallCollector(ast.NodeVisitor):
    """
    AST visitor to collect function calls within each function definition.
    Builds a mapping of caller to list of callees.
    """
    def __init__(self):
        self.calls = {}
        self.current_funcs = []

    def visit_FunctionDef(self, node):
        self.current_funcs.append(node.name)
        self.calls[node.name] = []
        self.generic_visit(node)
        self.current_funcs.pop()

    def visit_Call(self, node):
        if self.current_funcs and isinstance(node.func, ast.Name):
            self.calls[self.current_funcs[-1]].append(node.func.id)
        self.generic_visit(node)

def collect_function_calls(tree):
    """
    Uses CallCollector to collect function calls.
    Args:
        tree (ast.Module): The AST tree.
    Returns:
        dict: {caller_func: [list of called_funcs]}
    """
    collector = CallCollector()
    collector.visit(tree)
    return collector.calls