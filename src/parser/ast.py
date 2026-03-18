# src/parser/ast.py

class ASTNode:
    """Abstract base node"""
    def __init__(self, line=None, column=None):
        self.line = line
        self.column = column

class ProgramNode(ASTNode):
    def __init__(self, declarations, line=1, column=1):
        super().__init__(line, column)
        self.declarations = declarations

# --- Declarations (AST-4) ---
class DeclarationNode(ASTNode): pass

class FunctionDeclNode(DeclarationNode):
    def __init__(self, name, return_type, params, body, line=None, column=None):
        super().__init__(line, column)
        self.name = name
        self.return_type = return_type
        self.params = params # List[ParamNode]
        self.body = body     # BlockStmtNode

class StructDeclNode(DeclarationNode):
    def __init__(self, name, fields, line=None, column=None):
        super().__init__(line, column)
        self.name = name
        self.fields = fields # List[VarDeclStmtNode]

class ParamNode(ASTNode):
    def __init__(self, type_name, name, line=None, column=None):
        super().__init__(line, column)
        self.type_name = type_name
        self.name = name

# --- Statements (AST-3) ---
class StatementNode(ASTNode): pass

class BlockStmtNode(StatementNode):
    def __init__(self, statements, line=None, column=None):
        super().__init__(line, column)
        self.statements = statements

class VarDeclStmtNode(StatementNode):
    def __init__(self, type_name, name, initializer, line=None, column=None):
        super().__init__(line, column)
        self.type_name = type_name
        self.name = name
        self.initializer = initializer

class IfStmtNode(StatementNode):
    def __init__(self, condition, then_branch, else_branch, line=None, column=None):
        super().__init__(line, column)
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class WhileStmtNode(StatementNode):
    def __init__(self, condition, body, line=None, column=None):
        super().__init__(line, column)
        self.condition = condition
        self.body = body

class ForStmtNode(StatementNode):
    def __init__(self, init, condition, update, body, line=None, column=None):
        super().__init__(line, column)
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

class ReturnStmtNode(StatementNode):
    def __init__(self, value, line=None, column=None):
        super().__init__(line, column)
        self.value = value

class ExprStmtNode(StatementNode):
    def __init__(self, expression, line=None, column=None):
        super().__init__(line, column)
        self.expression = expression

# --- Expressions (AST-2) ---
class ExpressionNode(ASTNode): pass

class LiteralExprNode(ExpressionNode):
    def __init__(self, value, literal_type, line=None, column=None):
        super().__init__(line, column)
        self.value = value
        self.literal_type = literal_type

class IdentifierExprNode(ExpressionNode):
    def __init__(self, name, line=None, column=None):
        super().__init__(line, column)
        self.name = name

class BinaryExprNode(ExpressionNode):
    def __init__(self, left, operator, right, line=None, column=None):
        super().__init__(line, column)
        self.left = left
        self.operator = operator # Token object
        self.right = right

class UnaryExprNode(ExpressionNode):
    def __init__(self, operator, operand, line=None, column=None):
        super().__init__(line, column)
        self.operator = operator
        self.operand = operand

class CallExprNode(ExpressionNode):
    def __init__(self, callee, arguments, line=None, column=None):
        super().__init__(line, column)
        self.callee = callee
        self.arguments = arguments

class AssignmentExprNode(ExpressionNode):
    def __init__(self, target, operator, value, line=None, column=None):
        super().__init__(line, column)
        self.target = target
        self.operator = operator
        self.value = value