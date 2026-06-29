from src.parser import parse_boolean_formula

def test_parser():
    expr = "(a + B) ^ C"
    ast = parse_boolean_formula(expr)
    print("AST for (a + B) ^ C:", ast)

    expr2 = "!a * (b + c)"
    ast2 = parse_boolean_formula(expr2)
    print("AST for !a * (b + c):", ast2)

    expr3 = "~(a ^ b) + c"
    ast3 = parse_boolean_formula(expr3)
    print("AST for ~(a ^ b) + c:", ast3)

if __name__ == "__main__":
    test_parser()
