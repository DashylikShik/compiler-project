"""IR Generator - converts decorated AST to IR"""

from typing import Dict, List, Optional, Any
from parser.ast import *
from semantic.symbol_table import SymbolTable, SymbolInfo, SymbolKind
from semantic.type_system import TypeSystem, Type, BaseType
from .ir_instructions import *
from .ir_printer import IRPrinter


class BasicBlock:
    """Simple basic block for IR"""
    def __init__(self, label: str):
        self.label = label
        self.instructions: List[Instruction] = []
        self.predecessors = []
        self.successors = []
    
    def add_instruction(self, instr: Instruction):
        self.instructions.append(instr)
    
    def is_terminated(self) -> bool:
        if not self.instructions:
            return False
        last = self.instructions[-1]
        return last.type in [
            InstructionType.JUMP,
            InstructionType.JUMP_IF,
            InstructionType.JUMP_IF_NOT,
            InstructionType.RETURN
        ]


class IRGenerator:
    """Generates IR from decorated AST"""
    
    def __init__(self, symbol_table: SymbolTable, type_system: TypeSystem):
        self.symbol_table = symbol_table
        self.type_system = type_system
        self.program = IRProgram()
        self.current_function: Optional[IRFunction] = None
        self.current_block: Optional[BasicBlock] = None
        self.var_to_temp: Dict[str, Operand] = {}
        self.array_dimensions: Dict[str, List[int]] = {}
        self.array_params = set()
    
    def generate(self, ast: ProgramNode) -> IRProgram:
        """Generate IR for entire program"""
        for decl in ast.declarations:
            if isinstance(decl, FunctionDeclNode):
                self.visit_function(decl)
        return self.program
    
    def visit_function(self, node: FunctionDeclNode):
        """Generate IR for a function"""
        # Create IR function
        return_type = self.type_system.get_type(node.return_type)
        if return_type is None:
            return_type = Type(BaseType.INT)
            
        ir_func = IRFunction(
            name=node.name,
            return_type=return_type,
            parameters=[(p.name, self.type_system.get_type(p.type_name)) 
                       for p in node.params]
        )
        
        self.current_function = ir_func
        self.var_to_temp.clear()
        self.array_dimensions.clear()
        self.array_params.clear()
        
        # Create entry block
        self.current_block = BasicBlock("entry")
        ir_func.basic_blocks.append(self.current_block)
        
        for param in node.params:
            if "[]" in param.type_name or param.type_name.endswith("*"):
                self.array_params.add(param.name)
                # Использовать var напрямую, не temp
                self.var_to_temp[param.name] = Operand.var(param.name)
            else:
                temp = ir_func.new_temp()
                self.var_to_temp[param.name] = temp
                self.current_block.add_instruction(
                    Instruction(InstructionType.MOVE, temp, Operand.var(param.name))
                )
                # Generate code for body
        if node.body:
            self.visit_block(node.body)
        
        # Add implicit return if needed
        if not self.current_block.is_terminated():
            if return_type.base == BaseType.VOID:
                self.current_block.add_instruction(
                    Instruction(InstructionType.RETURN)
                )
            else:
                self.current_block.add_instruction(
                    Instruction(InstructionType.RETURN, src1=Operand.const(0))
                )
        
        self.program.add_function(ir_func)
        self.current_function = None
        self.current_block = None
    
    def visit_block(self, node: BlockStmtNode):
        """Generate IR for a block"""
        for stmt in node.statements:
            self.visit_statement(stmt)
    
    def visit_statement(self, node: StatementNode):
        """Generate IR for a statement"""
        if isinstance(node, ArrayDeclNode):
            self.visit_array_decl(node)
        elif isinstance(node, VarDeclStmtNode):
            self.visit_var_decl(node)
        elif isinstance(node, ExprStmtNode):
            self.visit_expression(node.expression)
        elif isinstance(node, IfStmtNode):
            self.visit_if(node)
        elif isinstance(node, WhileStmtNode):
            self.visit_while(node)
        elif isinstance(node, ForStmtNode):
            self.visit_for(node)
        elif isinstance(node, ReturnStmtNode):
            self.visit_return(node)
        elif isinstance(node, BlockStmtNode):
            self.visit_block(node)
    
    def visit_var_decl(self, node: VarDeclStmtNode):
        """Generate IR for variable declaration"""
        temp = self.current_function.new_temp()
        self.var_to_temp[node.name] = temp
        
        if node.initializer:
            init_temp = self.visit_expression(node.initializer)
            if init_temp:
                self.current_block.add_instruction(
                    Instruction(InstructionType.MOVE, temp, init_temp)
                )
    

    def _const_int_value(self, expr, default: int = 1) -> int:
        """Extract integer value from a constant AST/IR expression where possible."""
        if isinstance(expr, LiteralExprNode):
            try:
                return int(expr.value)
            except Exception:
                return default
        if isinstance(expr, Operand) and expr.operand_type == "const":
            try:
                return int(expr.value)
            except Exception:
                return default
        return default

    def _array_total_count(self, dimensions) -> int:
        total = 1
        dims = dimensions if isinstance(dimensions, list) else [dimensions]
        for d in dims:
            total *= self._const_int_value(d, 1)
        return max(total, 1)

    def visit_array_decl(self, node: ArrayDeclNode):
        """Generate heap allocation for a local array.

        Sprint 7 rule: arrays are not allocated by ALLOCA/stack storage.  A local
        array variable is a pointer temporary; storage is malloc(count * sizeof(T)).
        """
        ptr = self.current_function.new_temp()
        self.var_to_temp[node.name] = ptr

        dimensions = getattr(node, 'size', 1)
        dims = dimensions if isinstance(dimensions, list) else [dimensions]
        dim_values = [self._const_int_value(d, 1) for d in dims]

        self.array_dimensions[node.name] = dim_values

        count = 1
        for d in dim_values:
            count *= d
        element_size = 4  # int/float are 4 bytes in this compiler
        total_bytes = count * element_size

        # malloc(total_bytes), result pointer in ptr
        self.current_block.add_instruction(
            Instruction(InstructionType.PARAM, src1=Operand.const(0), src2=Operand.const(total_bytes))
        )
        self.current_block.add_instruction(
            Instruction(InstructionType.CALL, ptr, src1=Operand.var('malloc'), args=[Operand.const(total_bytes)])
        )

        # Optional initializer: int a[3] = {1, 2, 3};
        initializer = getattr(node, 'initializer', None)
        if isinstance(initializer, list):
            for i, value_expr in enumerate(initializer):
                value = self.visit_expression(value_expr)
                self.current_block.add_instruction(
                    Instruction(InstructionType.ARRAY_STORE, dest=ptr, src1=Operand.const(i), src2=value)
                )

    def _array_base_name(self, node):
        if isinstance(node, IdentifierExprNode):
            return node.name
        if isinstance(node, ArrayAccessNode):
            return self._array_base_name(node.array)
        return None

    def _flatten_array_access(self, node: ArrayAccessNode):
        indices = []
        cur = node

        while isinstance(cur, ArrayAccessNode):
            indices.append(cur.index)
            cur = cur.array

        indices.reverse()

        if not isinstance(cur, IdentifierExprNode):
            return None, None, None

        name = cur.name
        base = self.visit_identifier(cur)
        dims = self.array_dimensions.get(name)

        # arr[] parameter: это уже указатель, работаем как с 1D массивом
        if name in self.array_params:
            # base = Operand.var(name) → x86 возьмёт rdi/rsi напрямую
            index = self.visit_expression(indices[0])
            return Operand.var(name), index, name

        if not dims or len(indices) <= 1:
            index = self.visit_expression(indices[0])
            return base, index, name

        flat = None

        for i, idx_expr in enumerate(indices):
            idx = self.visit_expression(idx_expr)

            multiplier = 1
            for d in dims[i + 1:]:
                multiplier *= d

            if multiplier != 1:
                mul_temp = self.current_function.new_temp()
                self.current_block.add_instruction(
                    Instruction(
                        InstructionType.MUL,
                        mul_temp,
                        idx,
                        Operand.const(multiplier)
                    )
                )
                term = mul_temp
            else:
                term = idx

            if flat is None:
                flat = term
            else:
                add_temp = self.current_function.new_temp()
                self.current_block.add_instruction(
                    Instruction(
                        InstructionType.ADD,
                        add_temp,
                        flat,
                        term
                    )
                )
                flat = add_temp

        return base, flat, name

    def visit_array_access(self, node: ArrayAccessNode) -> Operand:
        base, index, _name = self._flatten_array_access(node)

        if base is None:
            base = self.visit_expression(node.array)
            index = self.visit_expression(node.index)

        result = self.current_function.new_temp()
        self.current_block.add_instruction(
            Instruction(InstructionType.ARRAY_LOAD, result, base, index)
        )
        return result

    def visit_array_assignment(self, node: ArrayAssignmentNode) -> Operand:
        fake_access = ArrayAccessNode(
            node.array,
            node.index,
            node.line,
            node.column
        )

        base, index, _name = self._flatten_array_access(fake_access)

        if base is None:
            base = self.visit_expression(node.array)
            index = self.visit_expression(node.index)

        value = self.visit_expression(node.value)

        self.current_block.add_instruction(
            Instruction(InstructionType.ARRAY_STORE, dest=base, src1=index, src2=value)
        )

        return value

    def visit_expression(self, node: ExpressionNode) -> Optional[Operand]:
        """Generate IR for expression and return result operand"""
        if isinstance(node, LiteralExprNode):
            return self.visit_literal(node)
        elif isinstance(node, IdentifierExprNode):
            return self.visit_identifier(node)
        elif isinstance(node, BinaryExprNode):
            return self.visit_binary(node)
        elif isinstance(node, UnaryExprNode):
            return self.visit_unary(node)
        elif isinstance(node, CallExprNode):
            return self.visit_call(node)
        elif isinstance(node, AssignmentExprNode):
            return self.visit_assignment(node)
        elif isinstance(node, ArrayAccessNode):
            return self.visit_array_access(node)
        elif isinstance(node, ArrayAssignmentNode):
            return self.visit_array_assignment(node)
        return None
    
    def visit_literal(self, node: LiteralExprNode) -> Operand:
        """Generate IR for literal"""
        if node.literal_type == "int":
            return Operand.const(int(node.value))
        elif node.literal_type == "float":
            return Operand.const(float(node.value))
        elif node.literal_type == "bool":
            return Operand.const(1 if node.value else 0)
        return Operand.const(node.value)
    
    def visit_identifier(self, node: IdentifierExprNode) -> Operand:
        """Generate IR for identifier"""
        if node.name in self.var_to_temp:
            return self.var_to_temp[node.name]
        return Operand.var(node.name)
    
    def visit_binary(self, node: BinaryExprNode) -> Operand:
        """Generate IR for binary operation with short-circuit for logical ops"""
        op = node.operator.lexeme
        
        # Short-circuit for && and ||
        if op == '&&':
            return self.visit_logical_and(node)
        elif op == '||':
            return self.visit_logical_or(node)
        
        # For arithmetic and comparison operators - normal evaluation
        left = self.visit_expression(node.left)
        right = self.visit_expression(node.right)
        result = self.current_function.new_temp()
        
        op_map = {
            '+': InstructionType.ADD,
            '-': InstructionType.SUB,
            '*': InstructionType.MUL,
            '/': InstructionType.DIV,
            '%': InstructionType.MOD,
            '==': InstructionType.CMP_EQ,
            '!=': InstructionType.CMP_NE,
            '<': InstructionType.CMP_LT,
            '<=': InstructionType.CMP_LE,
            '>': InstructionType.CMP_GT,
            '>=': InstructionType.CMP_GE,
        }
        
        inst_type = op_map.get(op, InstructionType.ADD)
        self.current_block.add_instruction(
            Instruction(inst_type, result, left, right)
        )
        return result

    def visit_logical_and(self, node: BinaryExprNode) -> Operand:
        """Generate short-circuit AND (&&)"""
        result = self.current_function.new_temp()
        false_label = self.current_function.new_label()
        end_label = self.current_function.new_label()
        
        # Вычисляем левый операнд
        left = self.visit_expression(node.left)
        
        # Если левый false -> прыжок на false_label
        self.current_block.add_instruction(
            Instruction(InstructionType.JUMP_IF_NOT, src1=left, src2=Operand.label(false_label))
        )
        
        # Вычисляем правый операнд (только если левый true)
        right = self.visit_expression(node.right)
        
        # Если правый false -> прыжок на false_label
        self.current_block.add_instruction(
            Instruction(InstructionType.JUMP_IF_NOT, src1=right, src2=Operand.label(false_label))
        )
        
        # Результат true
        self.current_block.add_instruction(
            Instruction(InstructionType.MOVE, result, Operand.const(1))
        )
        self.current_block.add_instruction(
            Instruction(InstructionType.JUMP, src1=Operand.label(end_label))
        )
        
        # Результат false
        false_block = BasicBlock(false_label)
        self.current_function.basic_blocks.append(false_block)
        self.current_block = false_block
        self.current_block.add_instruction(
            Instruction(InstructionType.MOVE, result, Operand.const(0))
        )
        
        # Конец
        self.current_block.add_instruction(
            Instruction(InstructionType.JUMP, src1=Operand.label(end_label))
        )
        
        end_block = BasicBlock(end_label)
        self.current_function.basic_blocks.append(end_block)
        self.current_block = end_block
        
        return result

    def visit_logical_or(self, node: BinaryExprNode) -> Operand:
        """Generate short-circuit OR (||)"""
        result = self.current_function.new_temp()
        true_label = self.current_function.new_label()
        end_label = self.current_function.new_label()
        
        # Вычисляем левый операнд
        left = self.visit_expression(node.left)
        
        # Если левый true -> прыжок на true_label
        self.current_block.add_instruction(
            Instruction(InstructionType.JUMP_IF, src1=left, src2=Operand.label(true_label))
        )
        
        # Вычисляем правый операнд (только если левый false)
        right = self.visit_expression(node.right)
        
        # Если правый true -> прыжок на true_label
        self.current_block.add_instruction(
            Instruction(InstructionType.JUMP_IF, src1=right, src2=Operand.label(true_label))
        )
        
        # Результат false
        self.current_block.add_instruction(
            Instruction(InstructionType.MOVE, result, Operand.const(0))
        )
        self.current_block.add_instruction(
            Instruction(InstructionType.JUMP, src1=Operand.label(end_label))
        )
        
        # Результат true
        true_block = BasicBlock(true_label)
        self.current_function.basic_blocks.append(true_block)
        self.current_block = true_block
        self.current_block.add_instruction(
            Instruction(InstructionType.MOVE, result, Operand.const(1))
        )
        
        # Конец
        self.current_block.add_instruction(
            Instruction(InstructionType.JUMP, src1=Operand.label(end_label))
        )
        
        end_block = BasicBlock(end_label)
        self.current_function.basic_blocks.append(end_block)
        self.current_block = end_block
        
        return result
    
    def visit_unary(self, node: UnaryExprNode) -> Operand:
        """Generate IR for unary operation"""
        operand = self.visit_expression(node.operand)
        result = self.current_function.new_temp()
        
        if node.operator.lexeme == '-':
            self.current_block.add_instruction(
                Instruction(InstructionType.NEG, result, operand)
            )
        elif node.operator.lexeme == '!':
            self.current_block.add_instruction(
                Instruction(InstructionType.NOT, result, operand)
            )
        else:
            return operand
        
        return result
    
    def visit_call(self, node: CallExprNode) -> Operand:
        """Generate IR for function call"""
        callee_name = None
        if isinstance(node.callee, IdentifierExprNode):
            callee_name = node.callee.name
        
        if not callee_name:
            return None
        
        # Generate arguments
        args = []
        for i, arg in enumerate(node.arguments):
            arg_temp = self.visit_expression(arg)
            if arg_temp:
                args.append(arg_temp)
                self.current_block.add_instruction(
                    Instruction(InstructionType.PARAM, src1=Operand.const(i), src2=arg_temp)
                )
        
        # Call instruction
        result = self.current_function.new_temp()
        self.current_block.add_instruction(
            Instruction(InstructionType.CALL, result, src1=Operand.var(callee_name), args=args)
        )
        
        return result
    
    def visit_assignment(self, node: AssignmentExprNode) -> Operand:
        """Generate IR for assignment"""
        target_name = None
        if isinstance(node.target, IdentifierExprNode):
            target_name = node.target.name
        
        value = self.visit_expression(node.value)
        
        if target_name and target_name in self.var_to_temp:
            temp = self.var_to_temp[target_name]
            self.current_block.add_instruction(
                Instruction(InstructionType.MOVE, temp, value)
            )
            return temp
        elif target_name:
            self.current_block.add_instruction(
                Instruction(InstructionType.STORE, src1=Operand.var(target_name), src2=value)
            )
            return value
        
        return value
    
    def visit_if(self, node: IfStmtNode):
        """Generate IR for if statement"""
        cond = self.visit_expression(node.condition)
        
        then_label = self.current_function.new_label()
        else_label = self.current_function.new_label()
        endif_label = self.current_function.new_label()
        
        # Conditional jump
        self.current_block.add_instruction(
            Instruction(InstructionType.JUMP_IF, src1=cond, src2=Operand.label(then_label))
        )
        self.current_block.add_instruction(
            Instruction(InstructionType.JUMP, src1=Operand.label(else_label))
        )
        
        # Then block
        then_block = BasicBlock(then_label)
        self.current_function.basic_blocks.append(then_block)
        self.current_block = then_block
        self.visit_statement(node.then_branch)
        if not self.current_block.is_terminated():
            self.current_block.add_instruction(
                Instruction(InstructionType.JUMP, src1=Operand.label(endif_label))
            )
        
        # Else block
        else_block = BasicBlock(else_label)
        self.current_function.basic_blocks.append(else_block)
        self.current_block = else_block
        if node.else_branch:
            self.visit_statement(node.else_branch)
        if not self.current_block.is_terminated():
            self.current_block.add_instruction(
                Instruction(InstructionType.JUMP, src1=Operand.label(endif_label))
            )
        
        # Endif block
        endif_block = BasicBlock(endif_label)
        self.current_function.basic_blocks.append(endif_block)
        self.current_block = endif_block
    
    def visit_while(self, node: WhileStmtNode):
        """Generate IR for while loop"""
        header_label = self.current_function.new_label()
        body_label = self.current_function.new_label()
        exit_label = self.current_function.new_label()
        
        # Jump to header
        self.current_block.add_instruction(
            Instruction(InstructionType.JUMP, src1=Operand.label(header_label))
        )
        
        # Header block
        header_block = BasicBlock(header_label)
        self.current_function.basic_blocks.append(header_block)
        self.current_block = header_block
        
        # Generate condition
        cond = self.visit_expression(node.condition)
        self.current_block.add_instruction(
            Instruction(InstructionType.JUMP_IF, src1=cond, src2=Operand.label(body_label))
        )
        self.current_block.add_instruction(
            Instruction(InstructionType.JUMP, src1=Operand.label(exit_label))
        )
        
        # Body block
        body_block = BasicBlock(body_label)
        self.current_function.basic_blocks.append(body_block)
        self.current_block = body_block
        self.visit_statement(node.body)
        
        # Jump back to header
        self.current_block.add_instruction(
            Instruction(InstructionType.JUMP, src1=Operand.label(header_label))
        )
        
        # Exit block
        exit_block = BasicBlock(exit_label)
        self.current_function.basic_blocks.append(exit_block)
        self.current_block = exit_block
    
    def visit_for(self, node: ForStmtNode):
        """Generate IR for for loop"""
        # Initialize
        if node.init:
            self.visit_statement(node.init)
        
        header_label = self.current_function.new_label()
        body_label = self.current_function.new_label()
        update_label = self.current_function.new_label()
        exit_label = self.current_function.new_label()
        
        # Jump to header
        self.current_block.add_instruction(
            Instruction(InstructionType.JUMP, src1=Operand.label(header_label))
        )
        
        # Header block
        header_block = BasicBlock(header_label)
        self.current_function.basic_blocks.append(header_block)
        self.current_block = header_block
        
        # Condition
        if node.condition:
            cond = self.visit_expression(node.condition)
            self.current_block.add_instruction(
                Instruction(InstructionType.JUMP_IF, src1=cond, src2=Operand.label(body_label))
            )
        else:
            self.current_block.add_instruction(
                Instruction(InstructionType.JUMP, src1=Operand.label(body_label))
            )
        self.current_block.add_instruction(
            Instruction(InstructionType.JUMP, src1=Operand.label(exit_label))
        )
        
        # Body block
        body_block = BasicBlock(body_label)
        self.current_function.basic_blocks.append(body_block)
        self.current_block = body_block
        self.visit_statement(node.body)
        
        # Jump to update
        self.current_block.add_instruction(
            Instruction(InstructionType.JUMP, src1=Operand.label(update_label))
        )
        
        # Update block
        update_block = BasicBlock(update_label)
        self.current_function.basic_blocks.append(update_block)
        self.current_block = update_block
        if node.update:
            self.visit_expression(node.update)
        
        # Jump back to header
        self.current_block.add_instruction(
            Instruction(InstructionType.JUMP, src1=Operand.label(header_label))
        )
        
        # Exit block
        exit_block = BasicBlock(exit_label)
        self.current_function.basic_blocks.append(exit_block)
        self.current_block = exit_block
    
    def visit_return(self, node: ReturnStmtNode):
        """Generate IR for return statement"""
        if node.value:
            value = self.visit_expression(node.value)
            if value:
                self.current_block.add_instruction(
                    Instruction(InstructionType.RETURN, src1=value)
                )
        else:
            self.current_block.add_instruction(
                Instruction(InstructionType.RETURN)
            )
    
    def get_program(self) -> IRProgram:
        return self.program