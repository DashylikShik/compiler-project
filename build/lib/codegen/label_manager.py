"""Label manager for unique label generation in control flow"""

class LabelManager:
    """Manages unique label generation for control flow"""
    
    def __init__(self):
        self.counter = 0
    
    def new_label(self, prefix: str = "L") -> str:
        """Generate a new unique label"""
        self.counter += 1
        return f"{prefix}{self.counter}"
    
    def reset(self):
        """Reset label counter (for new function)"""
        self.counter = 0
    
    def get_if_labels(self) -> tuple:
        """Generate labels for if-else statement"""
        return (self.new_label("L_then"), 
                self.new_label("L_else"), 
                self.new_label("L_endif"))
    
    def get_while_labels(self) -> tuple:
        """Generate labels for while loop"""
        return (self.new_label("L_while_cond"), 
                self.new_label("L_while_body"), 
                self.new_label("L_while_end"))
    
    def get_for_labels(self) -> tuple:
        """Generate labels for for loop"""
        return (self.new_label("L_for_init"),
                self.new_label("L_for_cond"),
                self.new_label("L_for_body"),
                self.new_label("L_for_update"),
                self.new_label("L_for_end"))
    
    def get_logical_labels(self) -> tuple:
        """Generate labels for logical operators"""
        return (self.new_label("L_logic_true"),
                self.new_label("L_logic_false"),
                self.new_label("L_logic_end"))