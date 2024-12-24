import ast

class TimeComplexityAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.loops = 0
        self.nested_loops = 0
        self.max_nested_loops = 0
        self.has_sort = False
        self.has_dict = False
        self.has_recursion = False
        self.current_functions = set()  # Track function definitions
        self.logarithmic_loops = False

    def visit_FunctionDef(self, node):
        # Add the function name to track possible recursion
        self.current_functions.add(node.name)
        self.generic_visit(node)
        self.current_functions.remove(node.name)

    def visit_For(self, node):
        self.loops += 1
        self.nested_loops += 1
        self.max_nested_loops = max(self.max_nested_loops, self.nested_loops)
        self.generic_visit(node)
        self.nested_loops -= 1

    def visit_While(self, node):
        self.loops += 1
        self.nested_loops += 1
        self.max_nested_loops = max(self.max_nested_loops, self.nested_loops)
        # Check for logarithmic patterns, e.g., `while x > 0: x //= 2`
        if isinstance(node.test, ast.Compare) and isinstance(node.body[0], ast.AugAssign):
            if isinstance(node.body[0].op, ast.FloorDiv):
                self.logarithmic_loops = True
        self.generic_visit(node)
        self.nested_loops -= 1

    def visit_Call(self, node):
        # Detect recursion
        if isinstance(node.func, ast.Name):
            if node.func.id in self.current_functions:  # Recursive function call
                self.has_recursion = True
        # Detect sort method
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'sort':
            self.has_sort = True
        self.generic_visit(node)

    def visit_Dict(self, node):
        self.has_dict = True
        self.generic_visit(node)


def analyze_time_complexity(code):
    try:
        tree = ast.parse(code)
        analyzer = TimeComplexityAnalyzer()
        analyzer.visit(tree)

        # Infer complexity based on detected patterns
        if analyzer.has_recursion:
            complexity = "O(2^n) or higher (recursion)"
        elif analyzer.max_nested_loops > 1:
            complexity = "O(n^2)"
        elif analyzer.logarithmic_loops:
            complexity = "O(log n)"
        elif analyzer.has_sort and analyzer.loops > 0:
            complexity = "O(n * log n)"
        elif analyzer.has_sort:
            complexity = "O(n log n)"
        elif analyzer.has_dict and analyzer.loops == 0:
            complexity = "O(1)"
        elif analyzer.loops > 0:
            complexity = "O(n)"
        else:
            complexity = "O(1)"

        return {
            "loops": analyzer.loops,
            "max_nested_loops": analyzer.max_nested_loops,
            "has_sort": analyzer.has_sort,
            "has_dict": analyzer.has_dict,
            "has_recursion": analyzer.has_recursion,
            "logarithmic_loops": analyzer.logarithmic_loops,
            "time_complexity": complexity
        }

    except Exception as e:
        return {"error": str(e)}


# Example usage
code_example = """
def example(arr):
    arr.sort()
    for i in arr:
        for j in range(len(arr)):
            pass
"""

result = analyze_time_complexity(code_example)
print(result)
