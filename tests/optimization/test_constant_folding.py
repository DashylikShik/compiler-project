#!/usr/bin/env python3
"""Tests for constant folding optimization"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.ir.ir_instructions import *
from src.ir.optimizer.constant_folding import ConstantFolding
from src.ir.ir_instructions import BasicBlock


class TestConstantFolding(unittest.TestCase):
    
    def test_fold_addition(self):
        """Test 2 + 3 → 5"""
        folding = ConstantFolding()
        
        # Create IR: t1 = ADD 2, 3
        prog = IRProgram()
        func = IRFunction("test", Type(BaseType.INT))
        block = BasicBlock("entry")
        instr = Instruction(InstructionType.ADD, 
                           dest=Operand.temp("t1"),
                           src1=Operand.const(2),
                           src2=Operand.const(3))
        block.add_instruction(instr)
        func.basic_blocks.append(block)
        prog.add_function(func)
        
        folding.optimize(prog)
        
        # After optimization: should be MOVE t1, 5
        new_instr = prog.functions[0].basic_blocks[0].instructions[0]
        self.assertEqual(new_instr.type, InstructionType.MOVE)
        self.assertEqual(new_instr.src1.value, 5)
        print(" test_fold_addition PASSED")
    
    def test_fold_multiplication(self):
        """Test 4 * 5 → 20"""
        folding = ConstantFolding()
        
        prog = IRProgram()
        func = IRFunction("test", Type(BaseType.INT))
        block = BasicBlock("entry")
        instr = Instruction(InstructionType.MUL,
                           dest=Operand.temp("t1"),
                           src1=Operand.const(4),
                           src2=Operand.const(5))
        block.add_instruction(instr)
        func.basic_blocks.append(block)
        prog.add_function(func)
        
        folding.optimize(prog)
        
        new_instr = prog.functions[0].basic_blocks[0].instructions[0]
        self.assertEqual(new_instr.type, InstructionType.MOVE)
        self.assertEqual(new_instr.src1.value, 20)
        print(" test_fold_multiplication PASSED")
    
    def test_no_fold_with_variable(self):
        """Test x + 3 should not be folded"""
        folding = ConstantFolding()
        
        prog = IRProgram()
        func = IRFunction("test", Type(BaseType.INT))
        block = BasicBlock("entry")
        instr = Instruction(InstructionType.ADD,
                           dest=Operand.temp("t1"),
                           src1=Operand.var("x"),
                           src2=Operand.const(3))
        block.add_instruction(instr)
        func.basic_blocks.append(block)
        prog.add_function(func)
        
        folding.optimize(prog)
        
        new_instr = prog.functions[0].basic_blocks[0].instructions[0]
        self.assertEqual(new_instr.type, InstructionType.ADD)
        print(" test_no_fold_with_variable PASSED")


if __name__ == "__main__":
    unittest.main()