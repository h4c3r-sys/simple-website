from src.parser import parse_boolean_formula
from src.composer import build_graph_from_ast

def test_composer():
    expr = "(a + B) ^ a"
    ast = parse_boolean_formula(expr)
    print("AST:", ast)

    graph = build_graph_from_ast(ast)
    print(f"Graph nodes: {len(graph.nodes())}")
    print(f"Graph edges: {len(graph.edges())}")

    # Check if 'a' and 'A' map to the same node
    variables = [n for n, d in graph.nodes(data=True) if d.get('type') == 'variable']
    print("Variable nodes:", variables)
    assert len(variables) == 2 # A and B

if __name__ == "__main__":
    test_composer()
