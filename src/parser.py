import re

class ASTNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

    def __repr__(self):
        if self.left and self.right:
            return f"({self.left} {self.value} {self.right})"
        elif self.left:
            return f"({self.value} {self.left})"
        else:
            return str(self.value)

def tokenize(expression):
    # Operators: +, *, &, !, ~, ^, (, )
    # Variables: letters and numbers
    tokens = []
    # Remove whitespace
    expression = expression.replace(" ", "")

    i = 0
    while i < len(expression):
        char = expression[i]
        if char in '+*&!~^()':
            tokens.append(char)
            i += 1
        elif char.isalnum():
            var = ""
            while i < len(expression) and expression[i].isalnum():
                var += expression[i]
                i += 1
            # Case insensitive variables
            tokens.append(var.upper())
        else:
            raise ValueError(f"Unknown character in expression: {char}")
    return tokens

def parse_boolean_formula(expression):
    tokens = tokenize(expression)

    precedence = {
        '!': 4, '~': 4,
        '*': 3, '&': 3,
        '^': 2,
        '+': 1,
        '(': 0
    }

    output_queue = []
    operator_stack = []

    for token in tokens:
        if token.isalnum():
            output_queue.append(ASTNode(token))
        elif token in '!~':
            operator_stack.append(token)
        elif token in '+*&^':
            while (operator_stack and operator_stack[-1] != '(' and
                   precedence[operator_stack[-1]] >= precedence[token]):
                op = operator_stack.pop()
                if op in '!~':
                    node = ASTNode(op, left=output_queue.pop())
                else:
                    right = output_queue.pop()
                    left = output_queue.pop()
                    node = ASTNode(op, left=left, right=right)
                output_queue.append(node)
            operator_stack.append(token)
        elif token == '(':
            operator_stack.append(token)
        elif token == ')':
            while operator_stack and operator_stack[-1] != '(':
                op = operator_stack.pop()
                if op in '!~':
                    node = ASTNode(op, left=output_queue.pop())
                else:
                    right = output_queue.pop()
                    left = output_queue.pop()
                    node = ASTNode(op, left=left, right=right)
                output_queue.append(node)
            if operator_stack and operator_stack[-1] == '(':
                operator_stack.pop()
            else:
                raise ValueError("Mismatched parentheses")

    while operator_stack:
        op = operator_stack.pop()
        if op == '(':
            raise ValueError("Mismatched parentheses")
        if op in '!~':
            node = ASTNode(op, left=output_queue.pop())
        else:
            right = output_queue.pop()
            left = output_queue.pop()
            node = ASTNode(op, left=left, right=right)
        output_queue.append(node)

    if len(output_queue) != 1:
        raise ValueError("Invalid expression")

    return output_queue[0]
