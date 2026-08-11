import networkx as nx
from src.gadgets import GADGET_DICT, VariableGadget

class GraphComposer:
    def __init__(self):
        self.composed_graph = nx.DiGraph()
        self.variables = {}  # Map of variable name -> VariableGadget
        self.gadget_counter = 0

    def _get_next_prefix(self, op):
        self.gadget_counter += 1
        return f"{op}_{self.gadget_counter}"

    def compose(self, ast_node):
        """
        Walks the AST, instantiates gadgets, connects them, and returns the 'output' node ID of the root gadget.
        """
        if ast_node is None:
            return None

        if ast_node.value.isalnum():
            # It's a variable
            var_name = ast_node.value
            if var_name not in self.variables:
                var_gadget = VariableGadget(f"var_{var_name}", var_name)
                self.variables[var_name] = var_gadget
                self.composed_graph = nx.compose(self.composed_graph, var_gadget.graph)

            # The "output" of a variable gadget is the node itself that we want to connect from
            return self.variables[var_name].output

        else:
            # It's an operator
            op = ast_node.value
            gadget_class = GADGET_DICT.get(op)
            if not gadget_class:
                raise ValueError(f"No gadget defined for operator: {op}")

            gadget = gadget_class(self._get_next_prefix(op))
            self.composed_graph = nx.compose(self.composed_graph, gadget.graph)

            # Unary operators
            if op in '!~':
                child_out = self.compose(ast_node.left)
                # Connect child's output to this gadget's input
                self.composed_graph.add_edge(child_out, gadget.inputs[0])
            else:
                # Binary operators
                left_out = self.compose(ast_node.left)
                right_out = self.compose(ast_node.right)

                # Connect children's outputs to this gadget's inputs
                self.composed_graph.add_edge(left_out, gadget.inputs[0])
                self.composed_graph.add_edge(right_out, gadget.inputs[1])

            return gadget.output

    def get_graph(self):
        return self.composed_graph

def build_graph_from_ast(ast_root):
    composer = GraphComposer()
    composer.compose(ast_root)
    return composer.get_graph()
