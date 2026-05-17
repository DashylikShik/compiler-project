"""System V AMD64 ABI constants and conventions"""

class ABI:
    """System V AMD64 ABI constants"""
    
    # Register mapping for 32-bit
    REG_32BIT = {
        'rax': 'eax', 'rbx': 'ebx', 'rcx': 'ecx', 'rdx': 'edx',
        'rdi': 'edi', 'rsi': 'esi', 'r8': 'r8d', 'r9': 'r9d',
        'r10': 'r10d', 'r11': 'r11d', 'r12': 'r12d', 'r13': 'r13d',
        'r14': 'r14d', 'r15': 'r15d'
    }
    
    # Argument passing registers (integer)
    INTEGER_ARG_REGS = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']
    
    # Floating point argument registers
    FLOAT_ARG_REGS = ['xmm0', 'xmm1', 'xmm2', 'xmm3', 'xmm4', 'xmm5', 'xmm6', 'xmm7']
    
    @classmethod
    def get_arg_register(cls, index: int, is_float: bool = False) -> str:
        """Get register for argument at position index"""
        if is_float:
            return cls.FLOAT_ARG_REGS[index] if index < len(cls.FLOAT_ARG_REGS) else None
        return cls.INTEGER_ARG_REGS[index] if index < len(cls.INTEGER_ARG_REGS) else None