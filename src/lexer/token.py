from enum import Enum

class TokenType(Enum):
    # Ключевые слова
    KW_INT = "int"
    KW_FLOAT = "float"
    KW_IF = "if"
    KW_ELSE = "else"
    KW_FOR = "for"
    KW_BOOL = "bool"
    KW_WHILE = "while"
    KW_RETURN = "return"
    KW_TRUE = "true"
    KW_FALSE = "false"
    KW_VOID = "void"
    KW_STRUCT = "struct"
    KW_FN = "fn"
    
    
    # Идентификаторы (имена переменных и функций)
    IDENTIFIER = "IDENTIFIER"
    
    # Литералы
    INT_LITERAL = "INT_LITERAL"
    FLOAT_LITERAL = "FLOAT_LITERAL"
    STRING_LITERAL = "STRING_LITERAL"  

    OP_PLUS = "+"
    OP_MINUS = "-"
    OP_MULT = "*"
    OP_DIV = "/"
    OP_MOD = "%" 
    OP_ASSIGN = "="
    OP_NOT = "!"   
    OP_AND = "&"             
    OP_OR = "|"   
    
    # Стрелка (для возвращаемого типа функции)
    OP_ARROW = "->"  
            
    
    # Операторы сравнения (два символа)
    OP_EQ = "=="
    OP_NEQ = "!="
    OP_LT = "<"
    OP_LTE = "<="             
    OP_GT = ">"
    OP_GTE = ">="             
    
    # Операторы присваивания (два символа)
    OP_PLUS_ASSIGN = "+="  
    OP_MINUS_ASSIGN = "-="    
    OP_MULT_ASSIGN = "*="  
    OP_DIV_ASSIGN = "/="  
    
    # Логические операторы (два символа)
    OP_AND_AND = "&&"  
    OP_OR_OR = "||"   
    
    # Разделители
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["  
    RBRACKET = "]"  
    SEMICOLON = ";"
    COMMA = ","
    COLON = ":"            
    
    # Специальные
    END_OF_FILE = "EOF"
    ERROR = "ERROR"

class Token:
    def __init__(self, type, lexeme, line, column, literal_value=None):
        self.type = type
        self.lexeme = lexeme
        self.line = line
        self.column = column
        self.literal_value = literal_value
    
    def __str__(self):
        if self.literal_value is not None:
            return f"{self.line}:{self.column} {self.type.value} \"{self.lexeme}\" {self.literal_value}"
        return f"{self.line}:{self.column} {self.type.value} \"{self.lexeme}\""
    
    def __repr__(self):
        return self.__str__()