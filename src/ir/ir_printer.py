"""IR printer for text output with DOT and JSON support"""

import json
from typing import List, Dict, Any
from .ir_instructions import IRProgram, IRFunction, Instruction, InstructionType, Operand


class IRPrinter:
    """Prints IR in human-readable format with DOT and JSON export"""
    
    @staticmethod
    def print_program(program: IRProgram) -> str:
        """Print entire IR program"""
        lines = ["# Generated IR for MiniCompiler"]
        
        for func in program.functions:
            lines.append(IRPrinter.print_function(func))
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def print_function(func: IRFunction) -> str:
        """Print function IR"""
        # Function signature
        params_str = ", ".join([f"{p[1]} {p[0]}" if len(p) > 1 and p[1] else str(p[0]) for p in func.parameters])
        lines = [
            f"func {func.name}({params_str}) -> {func.return_type}",
            "{"
        ]
        
        # Basic blocks
        block_count = len(func.basic_blocks)
        for idx, block in enumerate(func.basic_blocks):
            if block_count > 1:
                lines.append(f"  {block.label}:")
            for instr in block.instructions:
                instr_str = IRPrinter.format_instruction(instr)
                if instr_str:
                    lines.append(f"    {instr_str}")
            if idx < block_count - 1 and block_count > 1:
                lines.append("")
        
        lines.append("}")
        return "\n".join(lines)
    
    @staticmethod
    def format_instruction(instr: Instruction) -> str:
        """Format instruction for cleaner output"""
        if instr.type == InstructionType.COMMENT:
            return f"# {instr.comment}"
        elif instr.type == InstructionType.LABEL:
            return f"{instr.label}:"
        elif instr.type == InstructionType.JUMP:
            return f"jump {instr.src1}"
        elif instr.type == InstructionType.JUMP_IF:
            return f"jump_if {instr.src1}, {instr.src2}"
        elif instr.type == InstructionType.JUMP_IF_NOT:
            return f"jump_if_not {instr.src1}, {instr.src2}"
        elif instr.type == InstructionType.RETURN:
            return f"return {instr.src1}" if instr.src1 else "return"
        elif instr.type == InstructionType.MOVE:
            return f"{instr.dest} = {instr.src1}"
        elif instr.type == InstructionType.LOAD:
            return f"{instr.dest} = load {instr.src1}"
        elif instr.type == InstructionType.STORE:
            return f"store {instr.src1}, {instr.src2}"
        elif instr.type == InstructionType.CALL:
            args_str = ", ".join(str(a) for a in instr.args)
            if instr.dest:
                return f"{instr.dest} = call {instr.src1}({args_str})"
            return f"call {instr.src1}({args_str})"
        elif instr.type in [InstructionType.ADD, InstructionType.SUB, InstructionType.MUL, 
                           InstructionType.DIV, InstructionType.MOD, InstructionType.AND,
                           InstructionType.OR, InstructionType.XOR, InstructionType.CMP_EQ,
                           InstructionType.CMP_NE, InstructionType.CMP_LT, InstructionType.CMP_LE,
                           InstructionType.CMP_GT, InstructionType.CMP_GE]:
            return f"{instr.dest} = {instr.type.value} {instr.src1}, {instr.src2}"
        elif instr.type == InstructionType.NEG:
            return f"{instr.dest} = -{instr.src1}"
        elif instr.type == InstructionType.NOT:
            return f"{instr.dest} = !{instr.src1}"
        elif instr.type == InstructionType.PHI:
            args_str = ", ".join(str(a) for a in instr.args)
            return f"{instr.dest} = phi({args_str})"
        elif instr.type == InstructionType.PARAM:
            return f"param {instr.src2}"
        elif instr.type == InstructionType.ALLOCA:
            return f"{instr.dest} = alloca {instr.src1}"
        
        return str(instr)
    
    @staticmethod
    def to_dot(program: IRProgram) -> str:
        """Export IR to DOT format for Graphviz visualization"""
        lines = [
            "digraph IR {",
            "  rankdir=TB;",
            "  node [shape=box, style=filled, fillcolor=lightblue, fontname=\"Courier\"];",
            "  edge [arrowhead=vee];",
            ""
        ]
        
        for func in program.functions:
            lines.append(f"  subgraph cluster_{func.name} {{")
            lines.append(f"    label=\"Function: {func.name}\";")
            lines.append(f"    style=filled;")
            lines.append(f"    fillcolor=lightgrey;")
            lines.append(f"    color=black;")
            lines.append("")
            
            # Create nodes for each basic block
            for block in func.basic_blocks:
                # Build node label with instructions
                instr_lines = []
                for instr in block.instructions[:8]:  # Limit to 8 instructions
                    instr_str = IRPrinter.format_instruction(instr)
                    if instr_str:
                        # Escape special characters for DOT
                        instr_str = instr_str.replace('"', '\\"')
                        instr_lines.append(instr_str)
                
                if len(block.instructions) > 8:
                    instr_lines.append(f"... ({len(block.instructions) - 8} more)")
                
                label = f"{block.label}\\l" + "\\l".join(instr_lines) + "\\l"
                
                # Determine node color based on block type
                fillcolor = "lightblue"
                if block.label == "entry":
                    fillcolor = "lightgreen"
                elif block.label.startswith("L_"):
                    if "then" in block.label.lower():
                        fillcolor = "lightyellow"
                    elif "else" in block.label.lower():
                        fillcolor = "lightcoral"
                
                lines.append(f'    {block.label} [label="{label}", fillcolor={fillcolor}];')
            
            lines.append("")
            
            # Create edges for control flow
            for block in func.basic_blocks:
                terminator = block.get_terminator() if hasattr(block, 'get_terminator') else None
                
                if terminator:
                    if terminator.type == InstructionType.JUMP:
                        # Unconditional jump
                        target = str(terminator.src1)
                        lines.append(f'    {block.label} -> {target};')
                    
                    elif terminator.type == InstructionType.JUMP_IF:
                        # Conditional jump - true branch
                        target = str(terminator.src2)
                        lines.append(f'    {block.label} -> {target} [label="true", color=green];')
                        
                        # Fallthrough - find next block
                        idx = func.basic_blocks.index(block)
                        if idx + 1 < len(func.basic_blocks):
                            fallthrough = func.basic_blocks[idx + 1]
                            lines.append(f'    {block.label} -> {fallthrough.label} [label="false", color=red];')
                    
                    elif terminator.type == InstructionType.RETURN:
                        # Return node - add special styling
                        lines.append(f'    {block.label} -> return_{func.name} [style=dotted];')
            
            lines.append("  }")
            lines.append("")
        
        # Add return nodes
        lines.append("  node [shape=oval, fillcolor=lightgrey];")
        for func in program.functions:
            lines.append(f'  return_{func.name} [label="return {func.name}"];')
        
        lines.append("}")
        return "\n".join(lines)
    
    @staticmethod
    def to_json(program: IRProgram) -> Dict[str, Any]:
        """Export IR to JSON format for machine processing"""
        result = {
            "type": "IRProgram",
            "functions": []
        }
        
        for func in program.functions:
            func_dict = {
                "name": func.name,
                "return_type": str(func.return_type),
                "parameters": [],
                "basic_blocks": [],
                "temporaries": func.temp_counter,
                "statistics": {
                    "num_blocks": len(func.basic_blocks),
                    "num_instructions": sum(len(b.instructions) for b in func.basic_blocks)
                }
            }
            
            # Parameters
            for param in func.parameters:
                func_dict["parameters"].append({
                    "name": param[0],
                    "type": str(param[1]) if len(param) > 1 and param[1] else "unknown"
                })
            
            # Basic blocks
            for block in func.basic_blocks:
                block_dict = {
                    "label": block.label,
                    "instructions": [],
                    "predecessors": [],
                    "successors": []
                }
                
                # Instructions
                for instr in block.instructions:
                    instr_dict = {
                        "type": instr.type.value,
                        "dest": str(instr.dest) if instr.dest else None,
                        "src1": str(instr.src1) if instr.src1 else None,
                        "src2": str(instr.src2) if instr.src2 else None,
                        "args": [str(a) for a in instr.args] if instr.args else []
                    }
                    block_dict["instructions"].append(instr_dict)
                
                # Predecessors and successors
                if hasattr(block, 'predecessors'):
                    block_dict["predecessors"] = [p.label for p in block.predecessors]
                if hasattr(block, 'successors'):
                    block_dict["successors"] = [s.label for s in block.successors]
                
                func_dict["basic_blocks"].append(block_dict)
            
            result["functions"].append(func_dict)
        
        # Overall statistics
        result["statistics"] = {
            "total_functions": len(program.functions),
            "total_basic_blocks": sum(len(f.basic_blocks) for f in program.functions),
            "total_instructions": sum(
                len(b.instructions) for f in program.functions for b in f.basic_blocks
            ),
            "total_temporaries": sum(f.temp_counter for f in program.functions)
        }
        
        return result
    
    @staticmethod
    def to_json_string(program: IRProgram, indent: int = 2) -> str:
        """Export IR to JSON string"""
        return json.dumps(IRPrinter.to_json(program), indent=indent, ensure_ascii=False)
    
    @staticmethod
    def to_html(program: IRProgram) -> str:
        """Export IR to HTML format for browser viewing"""
        lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<title>IR Program</title>",
            "<style>",
            "  body { font-family: monospace; margin: 20px; }",
            "  .function { margin: 20px 0; border: 1px solid #ccc; border-radius: 5px; }",
            "  .function-header { background: #4CAF50; color: white; padding: 10px; }",
            "  .block { margin: 10px; border-left: 3px solid #2196F3; padding-left: 10px; }",
            "  .block-label { font-weight: bold; color: #2196F3; }",
            "  .instruction { font-family: monospace; margin: 5px 0; }",
            "  .stats { background: #f0f0f0; padding: 10px; border-radius: 5px; }",
            "</style>",
            "</head>",
            "<body>",
            "<h1>IR Program</h1>"
        ]
        
        # Statistics
        stats = IRPrinter.to_json(program)["statistics"]
        lines.append("<div class='stats'>")
        lines.append(f"<strong>Statistics:</strong><br>")
        lines.append(f"Functions: {stats['total_functions']}<br>")
        lines.append(f"Basic Blocks: {stats['total_basic_blocks']}<br>")
        lines.append(f"Instructions: {stats['total_instructions']}<br>")
        lines.append(f"Temporaries: {stats['total_temporaries']}")
        lines.append("</div>")
        
        # Functions
        for func in program.functions:
            lines.append(f"<div class='function'>")
            lines.append(f"<div class='function-header'><strong>func {func.name}</strong> ({func.return_type})</div>")
            
            for block in func.basic_blocks:
                lines.append(f"<div class='block'>")
                lines.append(f"<div class='block-label'>{block.label}:</div>")
                for instr in block.instructions:
                    instr_str = IRPrinter.format_instruction(instr)
                    lines.append(f"<div class='instruction'>{instr_str}</div>")
                lines.append(f"</div>")
            
            lines.append(f"</div>")
        
        lines.append("</body>")
        lines.append("</html>")
        
        return "\n".join(lines)