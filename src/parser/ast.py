from enum import Enum
from typing import List, Optional, Any

class NodeType(Enum):
    PROGRAM = "Program"
    FUNCTION_DECL = "FunctionDecl"
    STRUCT_DECL = "StructDecl"
    VAR_DECL = "VarDecl"
    PARAM = "Param"
    BLOCK = "Block"
    IF_STMT = "IfStmt"
    WHILE_STMT = "WhileStmt"
    FOR_STMT = "ForStmt"
    RETURN_STMT = "ReturnStmt"
    EXPR_STMT = "ExprStmt"
    BINARY_EXPR = "BinaryExpr"
    UNARY_EXPR = "UnaryExpr"
    LITERAL_EXPR = "LiteralExpr"
    IDENTIFIER_EXPR = "IdentifierExpr"
    CALL_EXPR = "CallExpr"
    ASSIGNMENT_EXPR = "AssignmentExpr"

class ASTNode:
    def __init__(self, line: int, column: int):
        self.line = line
        self.column = column
        self.node_type = None

class ProgramNode(ASTNode):
    def __init__(self, declarations: List[ASTNode], line: int = 1, column: int = 1):
        super().__init__(line, column)
        self.node_type = NodeType.PROGRAM
        self.declarations = declarations

# Declarations
class FunctionDeclNode(ASTNode):
    def __init__(self, name: str, params: List['ParamNode'], return_type: Optional[str], body: 'BlockNode', line: int, column: int):
        super().__init__(line, column)
        self.node_type = NodeType.FUNCTION_DECL
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body

class StructDeclNode(ASTNode):
    def __init__(self, name: str, fields: List['VarDeclNode'], line: int, column: int):
        super().__init__(line, column)
        self.node_type = NodeType.STRUCT_DECL
        self.name = name
        self.fields = fields

class VarDeclNode(ASTNode):
    def __init__(self, var_type: str, name: str, initializer: Optional['ExpressionNode'], line: int, column: int):
        super().__init__(line, column)
        self.node_type = NodeType.VAR_DECL
        self.var_type = var_type
        self.name = name
        self.initializer = initializer

class ParamNode(ASTNode):
    def __init__(self, param_type: str, name: str, line: int, column: int):
        super().__init__(line, column)
        self.node_type = NodeType.PARAM
        self.param_type = param_type
        self.name = name

# Statements
class BlockNode(ASTNode):
    def __init__(self, statements: List[ASTNode], line: int, column: int):
        super().__init__(line, column)
        self.node_type = NodeType.BLOCK
        self.statements = statements

class IfStmtNode(ASTNode):
    def __init__(self, condition: 'ExpressionNode', then_branch: ASTNode, else_branch: Optional[ASTNode], line: int, column: int):
        super().__init__(line, column)
        self.node_type = NodeType.IF_STMT
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class WhileStmtNode(ASTNode):
    def __init__(self, condition: 'ExpressionNode', body: ASTNode, line: int, column: int):
        super().__init__(line, column)
        self.node_type = NodeType.WHILE_STMT
        self.condition = condition
        self.body = body

class ForStmtNode(ASTNode):
    def __init__(self, init: Optional[ASTNode], condition: Optional['ExpressionNode'], update: Optional['ExpressionNode'], body: ASTNode, line: int, column: int):
        super().__init__(line, column)
        self.node_type = NodeType.FOR_STMT
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

class ReturnStmtNode(ASTNode):
    def __init__(self, value: Optional['ExpressionNode'], line: int, column: int):
        super().__init__(line, column)
        self.node_type = NodeType.RETURN_STMT
        self.value = value

class ExprStmtNode(ASTNode):
    def __init__(self, expression: 'ExpressionNode', line: int, column: int):
        super().__init__(line, column)
        self.node_type = NodeType.EXPR_STMT
        self.expression = expression

# Expressions
class ExpressionNode(ASTNode):
    pass

class LiteralExprNode(ExpressionNode):
    def __init__(self, value: Any, literal_type: str, line: int, column: int):
        super().__init__(line, column)
        self.node_type = NodeType.LITERAL_EXPR
        self.value = value
        self.literal_type = literal_type

class IdentifierExprNode(ExpressionNode):
    def __init__(self, name: str, line: int, column: int):
        super().__init__(line, column)
        self.node_type = NodeType.IDENTIFIER_EXPR
        self.name = name

class BinaryExprNode(ExpressionNode):
    def __init__(self, left: ExpressionNode, operator: str, right: ExpressionNode, line: int, column: int):
        super().__init__(line, column)
        self.node_type = NodeType.BINARY_EXPR
        self.left = left
        self.operator = operator
        self.right = right

class UnaryExprNode(ExpressionNode):
    def __init__(self, operator: str, operand: ExpressionNode, line: int, column: int):
        super().__init__(line, column)
        self.node_type = NodeType.UNARY_EXPR
        self.operator = operator
        self.operand = operand

class CallExprNode(ExpressionNode):
    def __init__(self, callee: str, arguments: List[ExpressionNode], line: int, column: int):
        super().__init__(line, column)
        self.node_type = NodeType.CALL_EXPR
        self.callee = callee
        self.arguments = arguments

class AssignmentExprNode(ExpressionNode):
    def __init__(self, target: str, operator: str, value: ExpressionNode, line: int, column: int):
        super().__init__(line, column)
        self.node_type = NodeType.ASSIGNMENT_EXPR
        self.target = target
        self.operator = operator
        self.value = value