import networkx as nx

class Gadget:
    """
    Base class for a graph gadget representing a boolean operation or variable.
    """
    def __init__(self, name_prefix):
        self.graph = nx.DiGraph()
        self.inputs = []
        self.output = None
        self.name_prefix = name_prefix

    def _add_node(self, node_id, label, node_type="internal"):
        full_id = f"{self.name_prefix}_{node_id}"
        self.graph.add_node(full_id, label=label, type=node_type)
        return full_id

    def _add_edge(self, source, target):
        self.graph.add_edge(source, target)


class VariableGadget(Gadget):
    def __init__(self, name_prefix, variable_name):
        super().__init__(name_prefix)
        self.output = self._add_node("out", variable_name, "variable")


class AndGadget(Gadget):
    """
    Placeholder for an AND gadget.
    In a real reduction (e.g. to 3-Coloring), this would be a more complex subgraph.
    """
    def __init__(self, name_prefix):
        super().__init__(name_prefix)
        # 2 inputs, 1 output, and an internal node
        self.inputs = [self._add_node("in1", "AND_in1", "input"),
                       self._add_node("in2", "AND_in2", "input")]
        internal = self._add_node("internal", "AND_core", "internal")
        self.output = self._add_node("out", "AND_out", "output")

        self._add_edge(self.inputs[0], internal)
        self._add_edge(self.inputs[1], internal)
        self._add_edge(internal, self.output)


class OrGadget(Gadget):
    """
    Placeholder for an OR gadget.
    """
    def __init__(self, name_prefix):
        super().__init__(name_prefix)
        self.inputs = [self._add_node("in1", "OR_in1", "input"),
                       self._add_node("in2", "OR_in2", "input")]
        internal = self._add_node("internal", "OR_core", "internal")
        self.output = self._add_node("out", "OR_out", "output")

        self._add_edge(self.inputs[0], internal)
        self._add_edge(self.inputs[1], internal)
        self._add_edge(internal, self.output)


class NotGadget(Gadget):
    """
    Placeholder for a NOT gadget.
    """
    def __init__(self, name_prefix):
        super().__init__(name_prefix)
        self.inputs = [self._add_node("in1", "NOT_in", "input")]
        internal = self._add_node("internal", "NOT_core", "internal")
        self.output = self._add_node("out", "NOT_out", "output")

        self._add_edge(self.inputs[0], internal)
        self._add_edge(internal, self.output)


class XorGadget(Gadget):
    """
    Placeholder for a XOR gadget (Symmetric Difference).
    Can easily be modified to include complex crossover nodes for planar graph reductions, etc.
    """
    def __init__(self, name_prefix):
        super().__init__(name_prefix)
        self.inputs = [self._add_node("in1", "XOR_in1", "input"),
                       self._add_node("in2", "XOR_in2", "input")]
        internal1 = self._add_node("int1", "XOR_core1", "internal")
        internal2 = self._add_node("int2", "XOR_core2", "internal")
        self.output = self._add_node("out", "XOR_out", "output")

        # Simple placeholder connections
        self._add_edge(self.inputs[0], internal1)
        self._add_edge(self.inputs[1], internal1)
        self._add_edge(self.inputs[0], internal2)
        self._add_edge(self.inputs[1], internal2)

        self._add_edge(internal1, self.output)
        self._add_edge(internal2, self.output)


# A dictionary to quickly map AST operators to their respective Gadget classes.
GADGET_DICT = {
    '+': OrGadget,
    '*': AndGadget,
    '&': AndGadget,
    '!': NotGadget,
    '~': NotGadget,
    '^': XorGadget
}
