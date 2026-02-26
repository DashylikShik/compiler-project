from .token import Token, TokenType

class Scanner:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        
        # Позиции в коде
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.start_column = 1
        
        
        self._token_index = 0
        # Ошибки
        self.errors = []
        
        # Ключевые слова
        self.keywords = {
            'int': TokenType.KW_INT,
            'float': TokenType.KW_FLOAT,
            'if': TokenType.KW_IF,
            'else': TokenType.KW_ELSE,
            'while': TokenType.KW_WHILE,
            'for': TokenType.KW_FOR,
            'return': TokenType.KW_RETURN,
            'true': TokenType.KW_TRUE,
            'false': TokenType.KW_FALSE,
            'void': TokenType.KW_VOID,
            'struct': TokenType.KW_STRUCT,
            'fn': TokenType.KW_FN,
            'bool': TokenType.KW_BOOL,
        }
        
        # Операторы (один символ)
        self.operators = {
            '+': TokenType.OP_PLUS,
            '-': TokenType.OP_MINUS,
            '*': TokenType.OP_MULT,
            '/': TokenType.OP_DIV,
            '%': TokenType.OP_MOD,
            '=': TokenType.OP_ASSIGN,
            '<': TokenType.OP_LT,
            '>': TokenType.OP_GT,
            '!': TokenType.OP_NOT,
            '&': TokenType.OP_AND,
            '|': TokenType.OP_OR,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            ';': TokenType.SEMICOLON,
            ',': TokenType.COMMA,
            ':': TokenType.COLON,
        }
        
        # Двухсимвольные операторы
        self.two_char_operators = {
            '==': TokenType.OP_EQ,
            '!=': TokenType.OP_NEQ,
            '<=': TokenType.OP_LTE,
            '>=': TokenType.OP_GTE,
            '&&': TokenType.OP_AND_AND,
            '||': TokenType.OP_OR_OR,
            '+=': TokenType.OP_PLUS_ASSIGN,
            '-=': TokenType.OP_MINUS_ASSIGN,
            '*=': TokenType.OP_MULT_ASSIGN,
            '/=': TokenType.OP_DIV_ASSIGN,
        }
        
        self.scan_tokens()
    
    #  ОСНОВНЫЕ МЕТОДЫ 
    def scan_tokens(self):
        """Сканирует все токены"""
        while not self.is_at_end():
            self.start = self.current
            self.start_column = self.column
            self.scan_token()
        
        self.tokens.append(Token(
            TokenType.END_OF_FILE, 
            "", 
            self.line, 
            self.column
        ))
        return self.tokens
    
    def scan_token(self):
        """Сканирует один токен"""
        char = self.advance()
        
        if char == ' ' or char == '\r' or char == '\t':
            pass  # пропускаем пробелы
        elif char == '\n':
            self.line += 1
            self.column = 1
        elif char == '"':
            self.scan_string()
        elif char.isdigit():
            self.scan_number()
        elif char.isalpha() or char == '_':
            self.scan_identifier()
        elif char == '/':
            if self.peek() == '/' or self.peek() == '*':
                self.scan_comment()
            else:
                self.scan_operator()
        else:
            self.scan_operator()
    
    #МЕТОДЫ ДЛЯ РАСПОЗНАВАНИЯ
    
    def scan_identifier(self):
        """Сканирует идентификатор или ключевое слово"""
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()
        
        text = self.source[self.start:self.current]
        
        # Проверяем длину
        if len(text) > 255:
            self.add_error(f"Идентификатор слишком длинный: {text[:50]}...")
        
        token_type = self.keywords.get(text, TokenType.IDENTIFIER)
        self.add_token(token_type)
    
    def scan_number(self):
        """Сканирует число (целое или с плавающей точкой)"""
        # Целая часть
        while self.peek().isdigit():
            self.advance()
        
        # Дробная часть
        if self.peek() == '.' and self.peek_next().isdigit():
            self.advance()  # точка
            while self.peek().isdigit():
                self.advance()
            
            value = float(self.source[self.start:self.current])
            self.add_token(TokenType.FLOAT_LITERAL, value)
        else:
            value = int(self.source[self.start:self.current])
            
            # Проверка диапазона
            if value < -2**31 or value > 2**31 - 1:
                self.add_error(f"Число {value} вне допустимого диапазона [-2³¹, 2³¹-1]")
            
            self.add_token(TokenType.INT_LITERAL, value)
    
    def scan_string(self):
        """Сканирует строковый литерал"""
        start_line = self.line
        start_col = self.start_column
        
        # Читаем символы до закрывающей кавычки или конца файла
        while not self.is_at_end() and self.peek() != '"':
            if self.peek() == '\n':
                self.line += 1
                self.column = 1
            self.advance()
        
        # Проверяем, почему вышли из цикла
        if self.is_at_end():
            # Достигнут конец файла без закрывающей кавычки
            value = self.source[self.start + 1:self.current]
            self.add_error("Незакрытая строка")
        else:
            # Нашли закрывающую кавычку
            self.advance()  # съедаем кавычку
            value = self.source[self.start + 1:self.current - 1]
        
        # Создаем токен
        token = Token(
            TokenType.STRING_LITERAL,
            self.source[self.start:self.current],
            start_line,
            start_col,
            value
        )
        self.tokens.append(token)
    
    def scan_comment(self):
        """Сканирует комментарии"""
        if self.peek() == '/':
            # Однострочный комментарий
            self.advance()  # второй 
            while self.peek() != '\n' and not self.is_at_end():
                self.advance()
        elif self.peek() == '*':
            # Многострочный комментарий
            self.advance()  # *
            nesting_level = 1
            
            while nesting_level > 0 and not self.is_at_end():
                if self.peek() == '*' and self.peek_next() == '/':
                    self.advance()  # *
                    self.advance()  # /
                    nesting_level -= 1
                elif self.peek() == '/' and self.peek_next() == '*':
                    self.advance()  # /
                    self.advance()  # *
                    nesting_level += 1
                else:
                    if self.peek() == '\n':
                        self.line += 1
                        self.column = 1
                    self.advance()
            
            if nesting_level > 0:
                self.add_error("Незакрытый многострочный комментарий")
    
    def scan_operator(self):
        """Сканирует операторы"""
        # Возвращаемся к началу оператора
        self.current = self.start
        self.column = self.start_column
        
        # Проверяем двухсимвольные операторы
        if not self.is_at_end() and self.current + 1 < len(self.source):
            two_char = self.source[self.current:self.current + 2]
            if two_char in self.two_char_operators:
                self.advance()
                self.advance()
                self.add_token(self.two_char_operators[two_char])
                return
        
        # Односимвольный оператор
        char = self.advance()
        if char in self.operators:
            self.add_token(self.operators[char])
        else:
            self.add_error(f"Неизвестный символ: '{char}'")
    
    #  ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    
    def add_token(self, token_type, literal_value=None):
        """Добавляет токен в список"""
        lexeme = self.source[self.start:self.current]
        token = Token(
            token_type,
            lexeme,
            self.line,
            self.start_column,
            literal_value
        )
        self.tokens.append(token)
    
    def add_error(self, message):
        """Добавляет ошибку"""
        error = f"Строка {self.line}, колонка {self.column}: {message}"
        self.errors.append(error)
    
    def advance(self):
        """Переходит к следующему символу и возвращает текущий"""
        char = self.source[self.current]
        self.current += 1
        self.column += 1
        return char
    
    def peek(self):
        """Смотрит на текущий символ без продвижения"""
        if self.is_at_end():
            return '\0'
        return self.source[self.current]
    
    def peek_next(self):
        """Смотрит на следующий символ без продвижения"""
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]
    
    def is_at_end(self):
        """Проверяет, достигнут ли конец файла"""
        return self.current >= len(self.source)
    
    #МЕТОДЫ ИНТЕРФЕЙСА
    
    def next_token(self):
        """Возвращает следующий токен и продвигается"""
        if self._token_index >= len(self.tokens):
            return Token(TokenType.END_OF_FILE, "", self.line, self.column)
        
        token = self.tokens[self._token_index]
        self._token_index += 1
        return token
    
    def peek_token(self):
        """Смотрит на следующий токен без продвижения"""
        if self._token_index >= len(self.tokens):
            return Token(TokenType.END_OF_FILE, "", self.line, self.column)
        
        return self.tokens[self._token_index]
    
    def get_line(self):
        """Возвращает текущую строку"""
        return self.line
    
    def get_column(self):
        """Возвращает текущую колонку"""
        return self.column
    
    def get_errors(self):
        """Возвращает список ошибок"""
        return self.errors