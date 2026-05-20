"""Control flow generation for if, while, for statements"""

from typing import List, Optional
from .label_manager import LabelManager


class ControlFlowGenerator:
    """Generates assembly for control flow statements"""
    
    def __init__(self, label_manager: LabelManager):
        self.label_manager = label_manager
        self.loop_stack = []  # Stack of active loops for break/continue
    
    def generate_if(self, condition_asm: List[str], then_asm: List[str], 
                    else_asm: Optional[List[str]] = None) -> List[str]:
        """Generate assembly for if-else statement"""
        then_label, else_label, endif_label = self.label_manager.get_if_labels()
        
        asm = []
        
        # Condition evaluation
        asm.extend(condition_asm)
        
        # Conditional jump to else (if condition false)
        asm.append(f"    cmp eax, 0")
        asm.append(f"    je {else_label}")
        
        # Then branch
        asm.append(f"{then_label}:")
        asm.extend(then_asm)
        asm.append(f"    jmp {endif_label}")
        
        # Else branch (optional)
        asm.append(f"{else_label}:")
        if else_asm:
            asm.extend(else_asm)
        
        # Endif merge point
        asm.append(f"{endif_label}:")
        
        return asm
    
    def generate_while(self, condition_asm: List[str], body_asm: List[str]) -> List[str]:
        """Generate assembly for while loop"""
        cond_label, body_label, end_label = self.label_manager.get_while_labels()
        
        # Push loop info for break/continue
        self.loop_stack.append({'cond': cond_label, 'end': end_label, 'body': body_label})
        
        asm = []
        asm.append(f"    jmp {cond_label}")
        
        # Loop body
        asm.append(f"{body_label}:")
        asm.extend(body_asm)
        
        # Condition check
        asm.append(f"{cond_label}:")
        asm.extend(condition_asm)
        asm.append(f"    cmp eax, 0")
        asm.append(f"    jne {body_label}")
        
        # Loop exit
        asm.append(f"{end_label}:")
        
        self.loop_stack.pop()
        return asm
    
    def generate_for(self, init_asm: List[str], condition_asm: List[str], 
                     update_asm: List[str], body_asm: List[str]) -> List[str]:
        """Generate assembly for for loop"""
        init_label, cond_label, body_label, update_label, end_label = self.label_manager.get_for_labels()
        
        # Push loop info
        self.loop_stack.append({'cond': cond_label, 'end': end_label, 'body': body_label})
        
        asm = []
        
        # Initialization
        asm.append(f"{init_label}:")
        asm.extend(init_asm)
        asm.append(f"    jmp {cond_label}")
        
        # Loop body
        asm.append(f"{body_label}:")
        asm.extend(body_asm)
        
        # Update
        asm.append(f"{update_label}:")
        asm.extend(update_asm)
        
        # Condition check
        asm.append(f"{cond_label}:")
        asm.extend(condition_asm)
        asm.append(f"    cmp eax, 0")
        asm.append(f"    jne {body_label}")
        
        # Loop exit
        asm.append(f"{end_label}:")
        
        self.loop_stack.pop()
        return asm
    
    def generate_break(self) -> List[str]:
        """Generate break statement (jump to loop exit)"""
        if not self.loop_stack:
            return ["; ERROR: break outside loop"]
        end_label = self.loop_stack[-1]['end']
        return [f"    jmp {end_label}"]
    
    def generate_continue(self) -> List[str]:
        """Generate continue statement (jump to loop condition)"""
        if not self.loop_stack:
            return ["; ERROR: continue outside loop"]
        cond_label = self.loop_stack[-1]['cond']
        return [f"    jmp {cond_label}"]