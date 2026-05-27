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

# Declarations (AST-4)
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

#Statements (AST-3)
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

# Expressions (AST-2)
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
        
class ArrayTypeNode(ASTNode):
    """Array type node"""
    def __init__(self, element_type, size, line=None, column=None):
        super().__init__(line, column)
        self.element_type = element_type  # TypeNode
        self.size = size  # int or None for unsized

class ArrayDeclNode(DeclarationNode):
    """Array declaration"""
    def __init__(self, type_node, name, size, initializer=None, line=None, column=None):
        super().__init__(line, column)
        self.type_node = type_node
        self.name = name
        self.size = size
        self.initializer = initializer  # list of expressions or None

class ArrayAccessNode(ExpressionNode):
    """Array access: arr[index]"""
    def __init__(self, array, index, line=None, column=None):
        super().__init__(line, column)
        self.array = array
        self.index = index

class ExternFunctionNode(DeclarationNode):
    """External function declaration"""
    def __init__(self, name, return_type, params, is_variadic, line=None, column=None):
        super().__init__(line, column)
        self.name = name
        self.return_type = return_type
        self.params = params
        self.is_variadic = is_variadic

# Sprint 7: Array nodes
class ArrayTypeNode(ASTNode):
    """Array type node: int[5]"""
    def __init__(self, element_type, size, line=None, column=None):
        super().__init__(line, column)
        self.element_type = element_type
        self.size = size

class ArrayDeclNode(DeclarationNode):
    """Array declaration: int arr[5] = {1,2,3}"""
    def __init__(self, type_name, name, size, initializer=None, line=None, column=None):
        super().__init__(line, column)
        self.type_name = type_name
        self.name = name
        self.size = size
        self.initializer = initializer

class ArrayAccessNode(ExpressionNode):
    """Array access: arr[i]"""
    def __init__(self, array, index, line=None, column=None):
        super().__init__(line, column)
        self.array = array
        self.index = index

class ArrayAssignmentNode(ExpressionNode):
    """Array assignment: arr[i] = value"""
    def __init__(self, array, index, operator, value, line=None, column=None):
        super().__init__(line, column)
        self.array = array
        self.index = index
        self.operator = operator
        self.value = value

class ExternFunctionNode(DeclarationNode):
    """External function declaration: extern int printf(char* format, ...);"""
    def __init__(self, name, return_type, params, is_variadic, line=None, column=None):
        super().__init__(line, column)
        self.name = name
        self.return_type = return_type
        self.params = params
        self.is_variadic = is_variadic