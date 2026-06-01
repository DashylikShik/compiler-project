from parser.ast import *

class ASTPrinter:
    INDENT_SIZE = 2

    @classmethod
    def print(cls, node: ASTNode, indent: int = 0) -> str:
        if node is None:
            return ""
        printer = cls()
        return printer._print_node(node, indent)

    def _indent(self, level: int) -> str:
        return " " * (level * self.INDENT_SIZE)

    def _print_node(self, node: ASTNode, indent: int) -> str:
        if isinstance(node, ProgramNode):
            return self._print_program(node, indent)
        if isinstance(node, FunctionDeclNode):
            return self._print_function(node, indent)
        if isinstance(node, StructDeclNode):
            return self._print_struct(node, indent)
        if isinstance(node, VarDeclStmtNode):
            return self._print_var_decl(node, indent)
        if isinstance(node, ParamNode):
            return self._print_param(node, indent)
        if isinstance(node, BlockStmtNode):
            return self._print_block(node, indent)
        if isinstance(node, IfStmtNode):
            return self._print_if(node, indent)
        if isinstance(node, WhileStmtNode):
            return self._print_while(node, indent)
        if isinstance(node, ForStmtNode):
            return self._print_for(node, indent)
        if isinstance(node, ReturnStmtNode):
            return self._print_return(node, indent)
        if isinstance(node, ExprStmtNode):
            return self._print_expr_stmt(node, indent)
        if isinstance(node, BinaryExprNode):
            return self._print_binary(node, indent)
        if isinstance(node, UnaryExprNode):
            return self._print_unary(node, indent)
        if isinstance(node, LiteralExprNode):
            return self._print_literal(node, indent)
        if isinstance(node, IdentifierExprNode):
            return self._print_identifier(node, indent)
        if isinstance(node, CallExprNode):
            return self._print_call(node, indent)
        if isinstance(node, AssignmentExprNode):
            return self._print_assignment(node, indent)
        return f"{self._indent(indent)}Unknown node: {type(node)}"

    def _print_program(self, node: ProgramNode, indent: int) -> str:
        lines = [f"{self._indent(indent)}Program:"]
        for decl in node.declarations:
            lines.append(self._print_node(decl, indent + 1))
        return "\n".join(lines)

    def _print_function(self, node: FunctionDeclNode, indent: int) -> str:
        return_type = f" -> {node.return_type}" if node.return_type else ""
        params = ", ".join([p.name for p in node.params])
        lines = [
            f"{self._indent(indent)}FunctionDecl: {node.name}{return_type}",
            f"{self._indent(indent + 1)}Parameters: [{params}]",
            f"{self._indent(indent + 1)}Body:"
        ]
        lines.append(self._print_node(node.body, indent + 2))
        return "\n".join(lines)

    def _print_struct(self, node: StructDeclNode, indent: int) -> str:
        lines = [f"{self._indent(indent)}StructDecl: {node.name}"]
        for field in node.fields:
            lines.append(self._print_node(field, indent + 1))
        return "\n".join(lines)

    def _print_var_decl(self, node: VarDeclStmtNode, indent: int) -> str:
        init = f" = {self._print_node(node.initializer, 0)}" if node.initializer else ""
        return f"{self._indent(indent)}VarDecl: {node.type_name} {node.name}{init}"

    def _print_param(self, node: ParamNode, indent: int) -> str:
        return f"{self._indent(indent)}Param: {node.type_name} {node.name}"

    def _print_block(self, node: BlockStmtNode, indent: int) -> str:
        lines = [f"{self._indent(indent)}Block:"]
        for stmt in node.statements:
            lines.append(self._print_node(stmt, indent + 1))
        return "\n".join(lines)

    def _print_if(self, node: IfStmtNode, indent: int) -> str:
        lines = [
            f"{self._indent(indent)}IfStmt:",
            f"{self._indent(indent + 1)}Condition: {self._print_node(node.condition, 0)}",
            f"{self._indent(indent + 1)}Then:"
        ]
        lines.append(self._print_node(node.then_branch, indent + 2))
        if node.else_branch:
            lines.append(f"{self._indent(indent + 1)}Else:")
            lines.append(self._print_node(node.else_branch, indent + 2))
        return "\n".join(lines)

    def _print_while(self, node: WhileStmtNode, indent: int) -> str:
        lines = [
            f"{self._indent(indent)}WhileStmt:",
            f"{self._indent(indent + 1)}Condition: {self._print_node(node.condition, 0)}",
            f"{self._indent(indent + 1)}Body:"
        ]
        lines.append(self._print_node(node.body, indent + 2))
        return "\n".join(lines)

    def _print_for(self, node: ForStmtNode, indent: int) -> str:
        lines = [f"{self._indent(indent)}ForStmt:"]
        if node.init:
            lines.append(f"{self._indent(indent + 1)}Init: {self._print_node(node.init, 0)}")
        if node.condition:
            lines.append(f"{self._indent(indent + 1)}Condition: {self._print_node(node.condition, 0)}")
        if node.update:
            lines.append(f"{self._indent(indent + 1)}Update: {self._print_node(node.update, 0)}")
        lines.append(f"{self._indent(indent + 1)}Body:")
        lines.append(self._print_node(node.body, indent + 2))
        return "\n".join(lines)

    def _print_return(self, node: ReturnStmtNode, indent: int) -> str:
        value = self._print_node(node.value, 0) if node.value else ""
        return f"{self._indent(indent)}Return: {value}"

    def _print_expr_stmt(self, node: ExprStmtNode, indent: int) -> str:
        return f"{self._indent(indent)}ExprStmt: {self._print_node(node.expression, 0)}"

    def _print_binary(self, node: BinaryExprNode, indent: int) -> str:
        left = self._print_node(node.left, 0)
        right = self._print_node(node.right, 0)
        return f"({left} {node.operator.lexeme} {right})"

    def _print_unary(self, node: UnaryExprNode, indent: int) -> str:
        operand = self._print_node(node.operand, 0)
        return f"({node.operator.lexeme}{operand})"

    def _print_literal(self, node: LiteralExprNode, indent: int) -> str:
        if node.literal_type == "string":
            return f'"{node.value}"'
        return str(node.value)

    def _print_identifier(self, node: IdentifierExprNode, indent: int) -> str:
        return node.name

    def _print_call(self, node: CallExprNode, indent: int) -> str:
        args = ", ".join([self._print_node(a, 0) for a in node.arguments])
        callee_name = node.callee.name if isinstance(node.callee, IdentifierExprNode) else str(node.callee)
        return f"{callee_name}({args})"

    def _print_assignment(self, node: AssignmentExprNode, indent: int) -> str:
        value = self._print_node(node.value, 0)
        target_name = node.target.name if isinstance(node.target, IdentifierExprNode) else str(node.target)
        return f"({target_name} {node.operator.lexeme} {value})"