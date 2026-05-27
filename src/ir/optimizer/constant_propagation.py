"""Constant propagation optimization pass"""

from ..ir_instructions import Instruction, InstructionType, Operand, IRProgram


class ConstantPropagation:
    """Propagates constant values through assignments"""
    
    def __init__(self):
        self.propagated_count = 0
        self.constants = {}
    
    def optimize(self, program: IRProgram) -> IRProgram:
        self.propagated_count = 0
        
        for func in program.functions:
            self.constants = {}
            for block in func.basic_blocks:
                self.optimize_block(block)
        
        return program
    
    def optimize_block(self, block):
        new_instructions = []
        for instr in block.instructions:
            # Track constant assignments
            if instr.type == InstructionType.MOVE:
                if self.is_constant(instr.src1):
                    self.constants[instr.dest.value] = self.get_const_value(instr.src1)
                    new_instructions.append(instr)
                else:
                    new_instructions.append(instr)
            else:
                # Propagate constants into instruction
                if instr.src1 and instr.src1.value in self.constants:
                    instr.src1 = Operand.const(self.constants[instr.src1.value])
                    self.propagated_count += 1
                if instr.src2 and instr.src2.value in self.constants:
                    instr.src2 = Operand.const(self.constants[instr.src2.value])
                    self.propagated_count += 1
                new_instructions.append(instr)
        
        block.instructions = new_instructions
    
    def is_constant(self, op: Operand) -> bool:
        return op is not None and op.operand_type == "const"
    
    def get_const_value(self, op: Operand):
        return op.value
    
    def get_stats(self):
        return {"constant_propagation": self.propagated_count}