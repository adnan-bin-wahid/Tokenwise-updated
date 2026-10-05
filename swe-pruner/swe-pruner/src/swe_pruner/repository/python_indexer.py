import ast
import copy
from pathlib import Path
from typing import Dict, List, Any, Set


def build_interface(tree: ast.Module) -> str | None:
    interface = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign, ast.AnnAssign)):
            interface.append(node)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            stub = copy.copy(node)
            stub.body = [ast.Expr(value=ast.Constant(value=Ellipsis))]
            interface.append(stub)
        elif isinstance(node, ast.ClassDef):
            stub = copy.copy(node)
            stub.body = []
            for child in node.body:
                if isinstance(child, (ast.Assign, ast.AnnAssign)):
                    stub.body.append(child)
                elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method = copy.copy(child)
                    method.body = [ast.Expr(value=ast.Constant(value=Ellipsis))]
                    stub.body.append(method)
            if not stub.body:
                stub.body = [ast.Expr(value=ast.Constant(value=Ellipsis))]
            interface.append(stub)
    return ast.unparse(ast.Module(body=interface, type_ignores=[])) if interface else None

class PythonASTIndexer:
    def index_file(self, file_path: Path, content: str | None = None) -> Dict[str, Any]:
        """
        Parses a single Python file using the ast module and extracts
        classes, functions, imports, and cross-reference calls.
        """
        try:
            if content is None:
                content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
        except Exception as e:
            return {"classes": {}, "functions": {}, "imports": [], "calls": [], "_signature": None}

        classes = {}
        functions = {}
        imports = []
        calls = []

        class SymbolVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_class = None

            def visit_Import(self, node: ast.Import):
                for name in node.names:
                    imports.append(name.name)
                self.generic_visit(node)

            def visit_ImportFrom(self, node: ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
                self.generic_visit(node)

            def visit_ClassDef(self, node: ast.ClassDef):
                prev_class = self.current_class
                self.current_class = node.name
                
                # Retrieve bases
                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        bases.append(base.attr)
                
                methods = []
                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        methods.append(child.name)
                
                classes[node.name] = {
                    "start_line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno),
                    "methods": methods,
                    "bases": bases,
                    "is_test": "test" in node.name.lower() or any("test" in b.lower() for b in bases)
                }
                
                self.generic_visit(node)
                self.current_class = prev_class

            def visit_FunctionDef(self, node: ast.FunctionDef):
                if self.current_class is None:
                    functions[node.name] = {
                        "start_line": node.lineno,
                        "end_line": getattr(node, "end_lineno", node.lineno),
                        "is_test": node.name.startswith("test_")
                    }
                self.generic_visit(node)

            def visit_Call(self, node: ast.Call):
                # Attempt to extract the name of the function or method being called
                if isinstance(node.func, ast.Name):
                    calls.append(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    calls.append(node.func.attr)
                self.generic_visit(node)

        visitor = SymbolVisitor()
        visitor.visit(tree)

        return {
            "classes": classes,
            "functions": functions,
            "imports": list(set(imports)),
            "calls": list(set(calls)),
            "_signature": build_interface(tree),
        }
