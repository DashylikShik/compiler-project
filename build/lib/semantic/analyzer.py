"""Semantic analyzer for MiniCompiler"""

from typing import List, Optional, Dict, Any
from parser.ast import *
from .symbol_table import SymbolTable, SymbolInfo, SymbolKind
from .type_system import TypeSystem, Type, BaseType, ArrayType
from .errors import *


class SemanticAnalyzer:
    """Performs semantic analysis on AST"""
    
    def __init__(self, verbose: bool = False):
        self.symbol_table = SymbolTable()
        self.type_system = TypeSystem()
        self.errors: List[SemanticError] = []
        self.verbose = verbose
        self.current_function: Optional[SymbolInfo] = None
        self.source_lines: Optional[List[str]] = None
        
        # Track initialized variables (basic)
        self.initialized_vars: set = set()
    
    def analyze(self, ast: ProgramNode, source: str = "") -> 'SemanticAnalyzer':
        """Perform semantic analysis on AST"""
        if source:
            self.source_lines = source.splitlines()
        
        # First pass: collect all declarations
        self.collect_declarations(ast)
        
        # Second pass: validate and analyze
        self.analyze_program(ast)
    
        return self
    
    def collect_declarations(self, node: ASTNode):
        """First pass: collect all declarations into symbol table"""
        if isinstance(node, ProgramNode):
            for decl in node.declarations:
                self.collect_declarations(decl)

        elif isinstance(node, FunctionDeclNode):

            existing = self.symbol_table.lookup_global(node.name)

            if existing:
                self.errors.append(
                    DuplicateDeclarationError(
                        node.name,
                        node.line,
                        node.column,
                        existing.line
                    )
                )
                return
            
            return_type = self.type_system.get_type(node.return_type)
            if not return_type:
                return_type = Type(BaseType.UNKNOWN)

            params = []
            for param in node.params:
                param_type = self.type_system.get_type(param.type_name)
                if not param_type:
                    param_type = Type(BaseType.UNKNOWN)

                param_info = SymbolInfo(
                    name=param.name,
                    kind=SymbolKind.PARAMETER,
                    type=param_type,
                    line=param.line,
                    column=param.column,
                    initialized=True
                )
                params.append(param_info)

            func_info = SymbolInfo(
                name=node.name,
                kind=SymbolKind.FUNCTION,
                type=return_type,
                line=node.line,
                column=node.column,
                initialized=True
            )

            func_info.return_type = return_type
            func_info.parameters = params
            func_info.is_variadic = False

            self.symbol_table.insert(node.name, func_info)

        elif isinstance(node, ExternFunctionNode):
            return_type = self.type_system.get_type(node.return_type)
            if not return_type:
                return_type = Type(BaseType.UNKNOWN)

            params = []
            for param in node.params:
                param_type = self.type_system.get_type(param.type_name)
                if not param_type:
                    param_type = Type(BaseType.UNKNOWN)

                param_info = SymbolInfo(
                    name=param.name,
                    kind=SymbolKind.PARAMETER,
                    type=param_type,
                    line=param.line,
                    column=param.column,
                    initialized=True
                )
                params.append(param_info)

            func_info = SymbolInfo(
                name=node.name,
                kind=SymbolKind.FUNCTION,
                type=return_type,
                line=node.line,
                column=node.column,
                initialized=True
            )

            func_info.return_type = return_type
            func_info.parameters = params
            func_info.is_variadic = getattr(node, "is_variadic", False)

            self.symbol_table.insert(node.name, func_info)
        
        elif isinstance(node, ArrayDeclNode):
            element_type = self.type_system.get_type(node.type_name)
            if not element_type:
                element_type = Type(BaseType.UNKNOWN)
                self.errors.append(SemanticError(
                    f"unknown type '{node.type_name}' for array",
                    node.line, node.column
                ))
            
            # Check for duplicate
            existing = self.symbol_table.lookup_local(node.name)
            if existing:
                self.errors.append(DuplicateDeclarationError(
                    node.name, node.line, node.column, existing.line
                ))
                return
            
            # Get array size safely
            size_value = 0
            if node.size:
                if hasattr(node.size, 'value'):
                    size_value = node.size.value
                elif isinstance(node.size, int):
                    size_value = node.size
                else:
                    size_value = 1
            
            # Register array variable
            var_info = SymbolInfo(
                name=node.name,
                kind=SymbolKind.VARIABLE,
                type=element_type,
                line=node.line,
                column=node.column,
                initialized=node.initializer is not None
            )

            # Sprint 7: сохранить размеры массива для проверки bounds
            sizes = []
            dims = node.size if isinstance(node.size, list) else [node.size]
            for dim in dims:
                if isinstance(dim, LiteralExprNode) and dim.literal_type == "int":
                    sizes.append(int(dim.value))
                elif hasattr(dim, "value"):
                    sizes.append(int(dim.value))

            var_info.array_sizes = sizes

            self.symbol_table.insert(node.name, var_info)

        
        elif isinstance(node, StructDeclNode):
            # Check for duplicate struct
            existing = self.symbol_table.lookup_global(node.name)
            if existing:
                self.errors.append(DuplicateDeclarationError(
                    node.name, node.line, node.column, existing.line
                ))
                return
            
            # Collect fields
            fields = {}
            for field in node.fields:
                field_type = self.type_system.get_type(field.type_name)
                if not field_type:
                    field_type = Type(BaseType.UNKNOWN)
                fields[field.name] = field_type
            
            struct_type = self.type_system.define_struct(node.name, fields)
            
            struct_info = SymbolInfo(
                name=node.name,
                kind=SymbolKind.STRUCT,
                type=struct_type,
                line=node.line,
                column=node.column,
                fields=fields
            )
            self.symbol_table.insert(node.name, struct_info)
        
        # Sprint 7: Array declaration
        elif isinstance(node, ArrayDeclNode):
            element_type = self.type_system.get_type(node.type_name)
            if not element_type:
                element_type = Type(BaseType.UNKNOWN)
                self.errors.append(SemanticError(
                    f"unknown type '{node.type_name}' for array",
                    node.line, node.column
                ))
            
            # Check for duplicate
            existing = self.symbol_table.lookup_local(node.name)
            if existing:
                self.errors.append(DuplicateDeclarationError(
                    node.name, node.line, node.column, existing.line
                ))
                return
            
            # Create array type
            array_type = ArrayType(element_type, node.size.value if hasattr(node.size, 'value') else 1)
            
            var_info = SymbolInfo(
                name=node.name,
                kind=SymbolKind.VARIABLE,
                type=element_type,  # Store element type for now
                line=node.line,
                column=node.column,
                initialized=node.initializer is not None
            )
            self.symbol_table.insert(node.name, var_info)
    
    def analyze_program(self, node: ProgramNode):
        """Second pass: analyze program"""
        for decl in node.declarations:
            self.analyze_declaration(decl)
    
    def analyze_declaration(self, node: DeclarationNode):
        """Analyze a declaration"""
        if isinstance(node, FunctionDeclNode):
            self.analyze_function(node)
        elif isinstance(node, StructDeclNode):
            self.analyze_struct(node)
        elif isinstance(node, VarDeclStmtNode):
            self.analyze_variable_declaration(node)
        elif isinstance(node, ArrayDeclNode):
            self.analyze_array_declaration(node)
    
    def analyze_array_declaration(self, node: ArrayDeclNode):
        """Analyze array declaration"""
        # Get element type
        element_type = self.type_system.get_type(node.type_name)
        if not element_type:
            element_type = Type(BaseType.UNKNOWN)
        
        # Analyze size expression
        if node.size:
            dims = node.size if isinstance(node.size, list) else [node.size]

            for dim in dims:
                size_type = self.analyze_expression(dim)

                if size_type and size_type.base != BaseType.INT:
                    self.errors.append(SemanticError(
                        f"array size must be integer, got {size_type}",
                        dim.line,
                        dim.column
                    ))
        
        # Analyze initializer if present
        if node.initializer:
            if isinstance(node.initializer, list):
                # Array initializer list
                for i, init_expr in enumerate(node.initializer):
                    init_type = self.analyze_expression(init_expr)
                    if not self.type_system.is_compatible(init_type, element_type):
                        self.errors.append(TypeMismatchError(
                            init_expr.line, init_expr.column,
                            str(element_type), str(init_type),
                            f" in array initializer at index {i}"
                        ))
            else:
                # Single initializer
                init_type = self.analyze_expression(node.initializer)
                if not self.type_system.is_compatible(init_type, element_type):
                    self.errors.append(TypeMismatchError(
                        node.line, node.column, str(element_type), str(init_type),
                        f" in initialization of array '{node.name}'"
                    ))

        existing = self.symbol_table.lookup_local(node.name)
        if not existing:
            var_info = SymbolInfo(
                name=node.name,
                kind=SymbolKind.VARIABLE,
                type=element_type,
                line=node.line,
                column=node.column,
                initialized=True
            )

            sizes = []
            dims = node.size if isinstance(node.size, list) else [node.size]
            for dim in dims:
                if isinstance(dim, LiteralExprNode) and dim.literal_type == "int":
                    sizes.append(int(dim.value))
                elif hasattr(dim, "value"):
                    sizes.append(int(dim.value))

            var_info.array_sizes = sizes
            self.symbol_table.insert(node.name, var_info)
    
    def analyze_function(self, node: FunctionDeclNode):
        """Analyze function declaration"""
        func_info = self.symbol_table.lookup_local(node.name)
        if not func_info:
            return
        
        self.current_function = func_info
        
        # Enter function scope
        self.symbol_table.enter_scope(f"function {node.name}")
        
        # Add parameters to function scope
        for param in node.params:
            param_type = self.type_system.get_type(param.type_name)
            if not param_type:
                param_type = Type(BaseType.UNKNOWN)
            
            param_info = SymbolInfo(
                name=param.name,
                kind=SymbolKind.PARAMETER,
                type=param_type,
                line=param.line,
                column=param.column,
                initialized=True
            )
            self.symbol_table.insert(param.name, param_info)
            self.initialized_vars.add(param.name)
        

        # Analyze function body
        if node.body:
            self.analyze_statement(node.body)
        
        self.symbol_table.exit_scope()
        self.current_function = None
        self.initialized_vars.clear()
    
    def analyze_struct(self, node: StructDeclNode):
        """Analyze struct declaration"""
        struct_info = self.symbol_table.lookup_global(node.name)
        if struct_info and struct_info.fields:
            field_names = set()
            for field in node.fields:
                if field.name in field_names:
                    self.errors.append(DuplicateDeclarationError(
                        field.name, field.line, field.column
                    ))
                field_names.add(field.name)
    
    def analyze_variable_declaration(self, node: VarDeclStmtNode):
        """Analyze variable declaration"""
        var_type = self.type_system.get_type(node.type_name)
        if not var_type:
            if node.type_name.endswith("*"):
                var_type = Type(BaseType.UNKNOWN)
            else:
                var_type = Type(BaseType.UNKNOWN)
                self.errors.append(SemanticError(
                    f"unknown type '{node.type_name}'", node.line, node.column
                ))
        # Check for duplicate in current scope
        existing = self.symbol_table.lookup_local(node.name)
        if existing:
            self.errors.append(DuplicateDeclarationError(
                node.name, node.line, node.column, existing.line
            ))
            return
        
        # Analyze initializer if present
        init_type = None
        if node.initializer:
            init_type = self.analyze_expression(node.initializer)
            
            # Type checking for initializer
            if init_type and init_type.base != BaseType.ERROR:
                if not self.type_system.is_compatible(init_type, var_type):
                    self.errors.append(TypeMismatchError(
                        node.line, node.column, str(var_type), str(init_type),
                        f" in initialization of '{node.name}'"
                    ))
        
        # Add variable to symbol table
        var_info = SymbolInfo(
            name=node.name,
            kind=SymbolKind.VARIABLE,
            type=var_type,
            line=node.line,
            column=node.column,
            initialized=init_type is not None
        )
        self.symbol_table.insert(node.name, var_info)
        
        if init_type and init_type.base != BaseType.ERROR:
            self.initialized_vars.add(node.name)
    
    def analyze_statement(self, node: StatementNode):
        """Analyze a statement"""
        if node is None:
            return
        
        if isinstance(node, BlockStmtNode):
            self.analyze_block(node)
        elif isinstance(node, VarDeclStmtNode):
            self.analyze_variable_declaration(node)
        elif isinstance(node, ArrayDeclNode):
            self.analyze_array_declaration(node)
        elif isinstance(node, IfStmtNode):
            self.analyze_if(node)
        elif isinstance(node, WhileStmtNode):
            self.analyze_while(node)
        elif isinstance(node, ForStmtNode):
            self.analyze_for(node)
        elif isinstance(node, ReturnStmtNode):
            self.analyze_return(node)
        elif isinstance(node, ExprStmtNode):
            self.analyze_expression(node.expression)
    
    def analyze_block(self, node: BlockStmtNode):
        """Analyze a block statement with its own scope"""
        self.symbol_table.enter_scope("block")
        saved_initialized = self.initialized_vars.copy()
        
        for stmt in node.statements:
            self.analyze_statement(stmt)
        
        self.initialized_vars = saved_initialized
        self.symbol_table.exit_scope()
    
    def analyze_if(self, node: IfStmtNode):
        """Analyze if statement"""
        cond_type = self.analyze_expression(node.condition)
        
        # Condition must be boolean
        if cond_type and cond_type.base != BaseType.ERROR:
            if cond_type.base != BaseType.BOOL:
                self.errors.append(InvalidConditionError(
                    node.condition.line, node.condition.column, str(cond_type)
                ))
        
        self.analyze_statement(node.then_branch)
        if node.else_branch:
            self.analyze_statement(node.else_branch)
    
    def analyze_while(self, node: WhileStmtNode):
        """Analyze while statement"""
        cond_type = self.analyze_expression(node.condition)
        
        if cond_type and cond_type.base != BaseType.ERROR:
            if cond_type.base != BaseType.BOOL:
                self.errors.append(InvalidConditionError(
                    node.condition.line, node.condition.column, str(cond_type)
                ))
        
        self.analyze_statement(node.body)
    
    def analyze_for(self, node: ForStmtNode):
        """Analyze for statement"""
        self.symbol_table.enter_scope("for")
        
        if node.init:
            self.analyze_statement(node.init)
        if node.condition:
            cond_type = self.analyze_expression(node.condition)
            if cond_type and cond_type.base != BaseType.BOOL:
                self.errors.append(InvalidConditionError(
                    node.condition.line, node.condition.column, str(cond_type)
                ))
        if node.update:
            self.analyze_expression(node.update)
        
        self.analyze_statement(node.body)
        
        self.symbol_table.exit_scope()
    
    def analyze_return(self, node: ReturnStmtNode):
        """Analyze return statement"""
        if not self.current_function:
            self.errors.append(SemanticError(
                "return statement outside function", node.line, node.column
            ))
            return
        
        expected_type = self.current_function.return_type
        
        if node.value:
            value_type = self.analyze_expression(node.value)
            
            if value_type and expected_type:
                if not self.type_system.is_compatible(value_type, expected_type):
                    self.errors.append(InvalidReturnTypeError(
                        node.line, node.column, str(expected_type), str(value_type)
                    ))
        else:
            # No value in return statement
            if expected_type and expected_type.base != BaseType.VOID:
                self.errors.append(InvalidReturnTypeError(
                    node.line, node.column, str(expected_type), "void"
                ))
    
    def analyze_expression(self, node: ExpressionNode) -> Type:
        """Analyze expression and return its type"""
        if node is None:
            return Type(BaseType.VOID)
        
        if isinstance(node, LiteralExprNode):
            return self.analyze_literal(node)
        elif isinstance(node, IdentifierExprNode):
            return self.analyze_identifier(node)
        elif isinstance(node, BinaryExprNode):
            return self.analyze_binary(node)
        elif isinstance(node, UnaryExprNode):
            return self.analyze_unary(node)
        elif isinstance(node, CallExprNode):
            return self.analyze_call(node)
        elif isinstance(node, AssignmentExprNode):
            return self.analyze_assignment(node)
        elif isinstance(node, ArrayAssignmentNode):
            array_type = self.analyze_array_access(
                ArrayAccessNode(node.array, node.index, node.line, node.column)
            )
            value_type = self.analyze_expression(node.value)

            if not self.type_system.is_compatible(value_type, array_type):
                self.errors.append(TypeMismatchError(
                    node.line, node.column, str(array_type), str(value_type),
                    " in array assignment"
                ))

            return array_type
        elif isinstance(node, ArrayAccessNode):
            return self.analyze_array_access(node)
        
        return Type(BaseType.UNKNOWN)
    
    def analyze_array_access(self, node: ArrayAccessNode) -> Type:
        """Analyze array access: arr[index], including constant bounds check"""

        base_node = node
        indices = []

        while isinstance(base_node, ArrayAccessNode):
            indices.append(base_node.index)
            base_node = base_node.array

        indices.reverse()

        if not isinstance(base_node, IdentifierExprNode):
            return Type(BaseType.ERROR)

        symbol = self.symbol_table.lookup(base_node.name)

        if not symbol:
            self.errors.append(SemanticError(
                f"undeclared array '{base_node.name}'",
                node.line, node.column
            ))
            return Type(BaseType.ERROR)

        for dim_index, index_expr in enumerate(indices):
            index_type = self.analyze_expression(index_expr)

            if index_type and index_type.base != BaseType.ERROR:
                if index_type.base != BaseType.INT:
                    self.errors.append(SemanticError(
                        f"array index must be integer, got {index_type}",
                        index_expr.line, index_expr.column
                    ))

            # Проверяем только константные индексы: arr[5]
            if isinstance(index_expr, LiteralExprNode) and index_expr.literal_type == "int":
                index_value = int(index_expr.value)
                sizes = getattr(symbol, "array_sizes", [])

                if dim_index < len(sizes):
                    size = sizes[dim_index]

                    if index_value < 0 or index_value >= size:
                        self.errors.append(SemanticError(
                            f"array index {index_value} out of bounds for array '{base_node.name}' of size {size}",
                            index_expr.line,
                            index_expr.column
                        ))

        return symbol.type
    
    def analyze_literal(self, node: LiteralExprNode) -> Type:
        """Analyze literal expression"""
        if node.literal_type == "int":
            return self.type_system.get_builtin('int')
        elif node.literal_type == "float":
            return self.type_system.get_builtin('float')
        elif node.literal_type == "string":
            return self.type_system.get_builtin('string')
        elif node.literal_type == "bool":
            return self.type_system.get_builtin('bool')
        
        return Type(BaseType.UNKNOWN)
    
    def analyze_identifier(self, node: IdentifierExprNode) -> Type:
        """Analyze identifier expression"""
        symbol = self.symbol_table.lookup(node.name)
        
        if not symbol:
            self.errors.append(UndeclaredIdentifierError(
                node.name, node.line, node.column
            ))
            return Type(BaseType.ERROR)
        
        # Check if variable is initialized (basic check)
        if symbol.kind == SymbolKind.VARIABLE and not symbol.initialized:
            if node.name not in self.initialized_vars:
                self.errors.append(SemanticError(
                    f"variable '{node.name}' may be uninitialized",
                    node.line, node.column
                ))
        
        return symbol.type
    
    def analyze_binary(self, node: BinaryExprNode) -> Type:
        """Analyze binary expression"""
        left_type = self.analyze_expression(node.left)
        right_type = self.analyze_expression(node.right)
        
        op = node.operator.lexeme
        result_type = self.type_system.get_binary_operator_result_type(
            op, left_type, right_type
        )

        if op in ("==", "!="):
            left_is_unknown = left_type.base == BaseType.UNKNOWN
            right_is_unknown = right_type.base == BaseType.UNKNOWN

            left_is_zero = isinstance(node.left, LiteralExprNode) and node.left.literal_type == "int" and int(node.left.value) == 0
            right_is_zero = isinstance(node.right, LiteralExprNode) and node.right.literal_type == "int" and int(node.right.value) == 0

            if (left_is_unknown and right_is_zero) or (right_is_unknown and left_is_zero):
                return self.type_system.get_builtin("bool")
        
        if result_type.base == BaseType.ERROR:
            self.errors.append(TypeMismatchError(
                node.line, node.column,
                f"valid types for '{op}'", f"{left_type} {op} {right_type}"
            ))
        
        return result_type
    
    def analyze_unary(self, node: UnaryExprNode) -> Type:
        """Analyze unary expression"""
        operand_type = self.analyze_expression(node.operand)
        
        op = node.operator.lexeme
        result_type = self.type_system.get_unary_operator_result_type(op, operand_type)
        
        if result_type.base == BaseType.ERROR:
            self.errors.append(TypeMismatchError(
                node.line, node.column,
                f"valid operand type for '{op}'", str(operand_type)
            ))
        
        return result_type
    
    def analyze_call(self, node: CallExprNode) -> Type:
        """Analyze function call"""
        # Callee should be an identifier
        callee_name = None
        if isinstance(node.callee, IdentifierExprNode):
            callee_name = node.callee.name
        
        if not callee_name:
            self.errors.append(SemanticError(
                "invalid function call", node.line, node.column
            ))
            return Type(BaseType.ERROR)
        
        # Look up function
        func_info = self.symbol_table.lookup(callee_name)
        if not func_info:
            self.errors.append(UndeclaredIdentifierError(
                callee_name, node.line, node.column
            ))
            return Type(BaseType.ERROR)
        
        if func_info.kind != SymbolKind.FUNCTION:
            self.errors.append(SemanticError(
                f"'{callee_name}' is not a function", node.line, node.column
            ))
            return Type(BaseType.ERROR)
        
        expected_count = len(func_info.parameters) if func_info.parameters else 0
        actual_count = len(node.arguments)
        is_variadic = getattr(func_info, "is_variadic", False)

        if is_variadic:
            # printf(char* format, ...) => минимум 1 обязательный аргумент
            if actual_count < expected_count:
                self.errors.append(SemanticError(
                    f"function '{callee_name}' expects at least {expected_count} arguments, got {actual_count}",
                    node.line,
                    node.column
                ))
                return func_info.return_type or Type(BaseType.UNKNOWN)
        else:
            if expected_count != actual_count:
                self.errors.append(ArgumentCountError(
                    node.line, node.column, expected_count, actual_count, callee_name
                ))
                return func_info.return_type or Type(BaseType.UNKNOWN)
        
        # Check argument types
        for i, (arg, param) in enumerate(zip(node.arguments, func_info.parameters)):
            arg_type = self.analyze_expression(arg)
            param_type = param.type

            # Sprint 7 extern support:
            # char*, void* и другие C pointer-типы у нас могут быть UNKNOWN,
            # поэтому для extern-функций не валим валидные printf/strcpy/malloc.
            if param_type.base == BaseType.UNKNOWN:
                continue

            if arg_type.base == BaseType.UNKNOWN:
                continue

            if not self.type_system.is_compatible(arg_type, param_type):
                self.errors.append(TypeMismatchError(
                    arg.line, arg.column, str(param_type), str(arg_type),
                    f" in argument {i+1} of '{callee_name}'"
                ))
        
        return func_info.return_type or Type(BaseType.UNKNOWN)
    
    def analyze_assignment(self, node: AssignmentExprNode) -> Type:
        """Analyze assignment expression"""
        # Target must be an identifier
        if not isinstance(node.target, IdentifierExprNode):
            self.errors.append(InvalidAssignmentTargetError(node.line, node.column))
            return Type(BaseType.ERROR)
        
        target_name = node.target.name
        target_symbol = self.symbol_table.lookup(target_name)
        
        if not target_symbol:
            self.errors.append(UndeclaredIdentifierError(
                target_name, node.line, node.column
            ))
            return Type(BaseType.ERROR)
        
        # Analyze value expression
        value_type = self.analyze_expression(node.value)
        
        # Check type compatibility
        if not self.type_system.is_compatible(value_type, target_symbol.type):
            self.errors.append(TypeMismatchError(
                node.line, node.column, str(target_symbol.type), str(value_type),
                f" in assignment to '{target_name}'"
            ))
        
        # Mark as initialized
        self.initialized_vars.add(target_name)
        
        return target_symbol.type
    
    def get_errors(self) -> List[SemanticError]:
        """Get list of semantic errors"""
        return self.errors
    
    def get_symbol_table(self) -> SymbolTable:
        """Get symbol table"""
        return self.symbol_table
    
    def get_decorated_ast(self) -> ASTNode:
        """Return decorated AST"""
        return None
    
    def has_errors(self) -> bool:
        """Check if any errors were found"""
        return len(self.errors) > 0
    
    def print_errors(self) -> None:
        """Print all errors with context"""
        for error in self.errors:
            formatted = error.format_with_context(self.source_lines)
            print(formatted)
            print()