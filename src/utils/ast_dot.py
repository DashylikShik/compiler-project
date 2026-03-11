from parser.ast import *

class ASTDotGenerator:
    @classmethod
    def generate(cls, node: ASTNode) -> str:
        generator = cls()
        lines = [
            "digraph AST {",
            "  rankdir=TB;",
            "  node [shape=box, style=filled, fillcolor=lightblue];",
            "  edge [arrowhead=vee];"
        ]
        generator._node_counter = 0
        generator._process_node(node, lines)
        lines.append("}")
        return "\n".join(lines)

    def _get_node_id(self) -> str:
        self._node_counter += 1
        return f"n{self._node_counter}"

    def _get_node_label(self, node: ASTNode) -> str:
        if isinstance(node, ProgramNode):
            return "Program"
        if isinstance(node, FunctionDeclNode):
            return f"Function\\n{node.name}"
        if isinstance(node, StructDeclNode):
            return f"Struct\\n{node.name}"
        if isinstance(node, VarDeclNode):
            init = " = ..." if node.initializer else ""
            return f"Var\\n{node.var_type} {node.name}{init}"
        if isinstance(node, ParamNode):
            return f"Param\\n{node.param_type} {node.name}"
        if isinstance(node, BlockNode):
            return "Block"
        if isinstance(node, IfStmtNode):
            return "If"
        if isinstance(node, WhileStmtNode):
            return "While"
        if isinstance(node, ForStmtNode):
            return "For"
        if isinstance(node, ReturnStmtNode):
            return "Return"
        if isinstance(node, ExprStmtNode):
            return "Expr"
        if isinstance(node, BinaryExprNode):
            return node.operator
        if isinstance(node, UnaryExprNode):
            return f"Unary\\n{node.operator}"
        if isinstance(node, LiteralExprNode):
            return f"Literal\\n{node.value}"
        if isinstance(node, IdentifierExprNode):
            return f"ID\\n{node.name}"
        if isinstance(node, CallExprNode):
            return f"Call\\n{node.callee}"
        if isinstance(node, AssignmentExprNode):
            return f"Assign\\n{node.operator}"
        return "Node"

    def _process_node(self, node: ASTNode, lines: list, parent_id: str = None) -> str:
        if node is None:
            return None
        node_id = self._get_node_id()
        label = self._get_node_label(node)
        lines.append(f'  {node_id} [label="{label}"];')
        if parent_id:
            lines.append(f'  {parent_id} -> {node_id};')

        if isinstance(node, ProgramNode):
            for decl in node.declarations:
                self._process_node(decl, lines, node_id)
        elif isinstance(node, FunctionDeclNode):
            for param in node.params:
                self._process_node(param, lines, node_id)
            self._process_node(node.body, lines, node_id)
        elif isinstance(node, StructDeclNode):
            for field in node.fields:
                self._process_node(field, lines, node_id)
        elif isinstance(node, BlockNode):
            for stmt in node.statements:
                self._process_node(stmt, lines, node_id)
        elif isinstance(node, IfStmtNode):
            cond_id = self._get_node_id()
            lines.append(f'  {cond_id} [label="Condition"];')
            lines.append(f'  {node_id} -> {cond_id};')
            self._process_node(node.condition, lines, cond_id)
            then_id = self._get_node_id()
            lines.append(f'  {then_id} [label="Then"];')
            lines.append(f'  {node_id} -> {then_id};')
            self._process_node(node.then_branch, lines, then_id)
            if node.else_branch:
                else_id = self._get_node_id()
                lines.append(f'  {else_id} [label="Else"];')
                lines.append(f'  {node_id} -> {else_id};')
                self._process_node(node.else_branch, lines, else_id)
        elif isinstance(node, WhileStmtNode):
            cond_id = self._get_node_id()
            lines.append(f'  {cond_id} [label="Condition"];')
            lines.append(f'  {node_id} -> {cond_id};')
            self._process_node(node.condition, lines, cond_id)
            body_id = self._get_node_id()
            lines.append(f'  {body_id} [label="Body"];')
            lines.append(f'  {node_id} -> {body_id};')
            self._process_node(node.body, lines, body_id)
        elif isinstance(node, BinaryExprNode):
            self._process_node(node.left, lines, node_id)
            self._process_node(node.right, lines, node_id)
        elif isinstance(node, UnaryExprNode):
            self._process_node(node.operand, lines, node_id)
        elif isinstance(node, CallExprNode):
            for arg in node.arguments:
                self._process_node(arg, lines, node_id)
        elif isinstance(node, AssignmentExprNode):
            self._process_node(node.value, lines, node_id)
        return node_id