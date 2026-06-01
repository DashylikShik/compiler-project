"""Constant folding optimization pass for Sprint 7"""

from ..ir_instructions import Instruction, InstructionType, Operand, IRProgram, IRFunction, BasicBlock



class ConstantFolding:
    """Folds constant expressions at compile time"""
    
    def __init__(self):
        self.folded_count = 0
    
    def optimize(self, program: IRProgram) -> IRProgram:
        """Apply constant folding to all functions"""
        self.folded_count = 0
        
        for func in program.functions:
            self.optimize_function(func)
        
        return program
    
    def optimize_function(self, func: IRFunction):
        """Optimize a single function"""
        for block in func.basic_blocks:
            new_instructions = []
            for instr in block.instructions:
                optimized = self.fold_instruction(instr)
                new_instructions.append(optimized)
            block.instructions = new_instructions
    
    def fold_instruction(self, instr: Instruction) -> Instruction:
        """Fold constant expressions"""
        if instr.type in [InstructionType.ADD, InstructionType.SUB, 
                          InstructionType.MUL, InstructionType.DIV]:
            if self.is_constant(instr.src1) and self.is_constant(instr.src2):
                left = self.get_const_value(instr.src1)
                right = self.get_const_value(instr.src2)
                
                if instr.type == InstructionType.ADD:
                    result = left + right
                elif instr.type == InstructionType.SUB:
                    result = left - right
                elif instr.type == InstructionType.MUL:
                    result = left * right
                elif instr.type == InstructionType.DIV:
                    if right != 0:
                        result = left // right
                    else:
                        return instr
                else:
                    return instr
                
                self.folded_count += 1
                return Instruction(
                    InstructionType.MOVE,
                    dest=instr.dest,
                    src1=Operand.const(result)
                )
        
        return instr
    
    def is_constant(self, op: Operand) -> bool:
        return op is not None and op.operand_type == "const"
    
    def get_const_value(self, op: Operand):
        return op.value
    
    def get_stats(self):
        return {"constant_folding": self.folded_count}