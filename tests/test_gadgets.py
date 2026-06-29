from src.gadgets import GADGET_DICT, VariableGadget

def test_gadgets():
    var_gadget = VariableGadget("var_A", "A")
    print("Variable nodes:", var_gadget.graph.nodes(data=True))

    and_gadget = GADGET_DICT['*']("and_0")
    print("AND nodes:", and_gadget.graph.nodes(data=True))
    print("AND edges:", and_gadget.graph.edges())

if __name__ == "__main__":
    test_gadgets()
