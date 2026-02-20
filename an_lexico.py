from tokens import Token
from token_types import TokenType
from errors import LexError

KEYWORDS = {
    "let": TokenType.LET,
    "int": TokenType.INT,
    "float": TokenType.FLOAT,
    "boolean": TokenType.BOOLEAN,
    "string": TokenType.STRING,
    "void": TokenType.VOID,
    "function": TokenType.FUNCTION,
    "return": TokenType.RETURN,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "do": TokenType.DO,
    "while": TokenType.WHILE,
    "read": TokenType.READ,
    "write": TokenType.WRITE,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
}

class Lexer:
    def __init__(self, source: str, symbols):
        self.source = source
        self.symbols = symbols
        self.tokens = []
        self.errors = []
        self.line = 1
        self.column = 1
        self.pos = 0
        self.current_function = None
        self._awaiting_function_body_of = None
        self._brace_depth = 0
        self._pending_param_names = set()


   
    def tokenize(self):
        
        while not self._is_at_end():
            
           
            if self.errors:
                break
            

            c = self._advance()

            # --- saltos de línea ---
            if c == "\n":
                self.line += 1
                self.column = 1
                continue

            # --- espacios y tabulaciones ---
            if c in " \t\r":
                self.column += 1
                continue

            # --- comentarios ---
            if c == "/" and self._peek() == "/":
                self._skip_comment()
                continue

            # --- identificadores o palabras clave ---
            if c.isalpha() or c == "_":
                self._identifier(c)
                continue

            # --- números ---
            if c.isdigit():
                self._number(c)
                continue

            # --- cadenas con comillas simples ---
            if c == "'":
                self._string()
                continue

            # --- operadores y símbolos ---
            self._operator_or_punctuator(c)

            
        if not self.errors:
            self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))

        
        return self.tokens, self.errors

    # ---------------- Rutinas auxiliares ----------------
    def _is_at_end(self):
        return self.pos >= len(self.source)

    def _advance(self):
        char = self.source[self.pos]
        self.pos += 1
        return char

    def _peek(self):
        if self._is_at_end():
            return "\0"
        return self.source[self.pos]

    # --- comentarios ---
    def _skip_comment(self):
        while not self._is_at_end() and self._peek() != "\n":
            self.pos += 1
        self.column = 1

    # --- identificadores / palabras clave ---
    def _identifier(self, first_char):
        start_pos = self.pos - 1
        start_col = self.column
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()
        lexeme = self.source[start_pos:self.pos]
        ttype = KEYWORDS.get(lexeme, TokenType.ID)

        if ttype == TokenType.ID:
            if self.current_function:
                
                ltab = self.symbols.locales.get(self.current_function)
                lentry = ltab.buscar(lexeme) if ltab else None
                if lentry:
                    entry = lentry
                else:
                    
                    gentry = self.symbols.buscar(lexeme)
                    if gentry:
                        entry = gentry
                    else:
                        
                        self.symbols.add_local(self.current_function, lexeme, "id")
                        entry = self.symbols.locales[self.current_function].buscar(lexeme)

            elif self._awaiting_function_body_of and lexeme in self._pending_param_names:
                
                fname = self._awaiting_function_body_of
                entry = self.symbols.locales[fname].buscar(lexeme)

            else:
                
                if hasattr(self.symbols, "locales") and lexeme in self.symbols.locales:
                    entry = (self.symbols.buscar(lexeme)
                            or self.symbols.add_if_absent(lexeme, self.line, "void", categoria="Función"))
                else:
                    entry = self.symbols.add_if_absent(lexeme, self.line)

            
            idx = getattr(entry, "index", "?")
            
            token = Token(ttype, lexeme, self.line, start_col, attribute=str(idx))
            
        else:
            token = Token(ttype, lexeme, self.line, start_col)

        self.tokens.append(token)
        self.column += len(lexeme)

        if ttype == TokenType.LET:
            self._propagate_type_declaration()
        elif ttype == TokenType.FUNCTION:
            self._propagate_function_declaration()

    # --- números ---
    def _number(self, first_char):
        start_col = self.column
        
        
        start_pos = self.pos - 1 
        valor = int(first_char)
        
        # 1. Parte Entera
        while self._peek().isdigit():
            c = self._advance()
            # Acumulamos matemáticamente: valor * 10 + digito
            valor = valor * 10 + int(c)

        # 2. Parte Decimal
        if self._peek() == ".":
            self._advance() 
            
            
            if not self._peek().isdigit():
                self._add_error("Número real mal formado (falta dígito tras '.')", start_col)
                return
            
            div = 10.0
            while self._peek().isdigit():
                c = self._advance()
                
                valor = valor + (int(c) / div)
                div = div * 10.0
            
            
            lexeme = self.source[start_pos:self.pos]
            
           
            if valor > 117549436.0:
                self._add_error(f"Real fuera de rango ({lexeme})", start_col)
            else:
               
                self.tokens.append(Token(TokenType.FLOAT_CONST, lexeme, self.line, start_col))
                
        else:
            
            lexeme = self.source[start_pos:self.pos]
            
            # Chequeo de rango ENTERO 
            if valor > 32767:
                self._add_error(f"Entero fuera de rango ({lexeme})", start_col)
            else:
                
                self.tokens.append(Token(TokenType.INT_CONST, lexeme, self.line, start_col))

        
        self.column += len(lexeme)

    # --- cadenas ---
    def _string(self):
        start_col = self.column
        start_pos = self.pos
        
        
        while not self._is_at_end() and self._peek() != "'":
            if self._peek() == "\n":
                self._add_error("Cadena no cerrada antes del salto de línea", start_col)
                return
            self._advance()
            
        if self._is_at_end():
            self._add_error("Cadena no cerrada al final del archivo", start_col)
            return
            
        self._advance()  
        
        lexeme_completo = self.source[start_pos - 1:self.pos]
        contenido = self.source[start_pos:self.pos - 1]
        
        if len(contenido) > 64:
            self._add_error(f"Cadena demasiado larga ({len(contenido)} caracteres). Máximo permitido: 64.", start_col)
            return
        
        self.tokens.append(Token(TokenType.STRING_CONST, lexeme_completo, self.line, start_col))
        self.column += len(lexeme_completo)

    # --- operadores / delimitadores ---
    def _operator_or_punctuator(self, c):
        start_col = self.column

        if c == "|" and self._peek() == "=":
            self._advance()
            self.tokens.append(Token(TokenType.OR_ASSIGN, "|=", self.line, start_col))
            self.column += 2
            return

        if c == "{":
            if self._awaiting_function_body_of and not self.current_function:
                self.current_function = self._awaiting_function_body_of
                self._awaiting_function_body_of = None
                self._brace_depth = 1
                self._pending_param_names.clear()  
            elif self.current_function:
                self._brace_depth += 1
            self.tokens.append(Token(TokenType.LBRACE, "{", self.line, start_col))
            self.column += 1
            return

        if c == "}":
            if self.current_function:
                self._brace_depth -= 1
                if self._brace_depth <= 0:
                    self.current_function = None
                    self._brace_depth = 0
            self.tokens.append(Token(TokenType.RBRACE, "}", self.line, start_col))
            self.column += 1
            return

        single_ops = {
            "+": TokenType.PLUS,
            "<": TokenType.LT,
            "!": TokenType.NOT,
            "=": TokenType.ASSIGN,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            ";": TokenType.SEMICOLON,
            ",": TokenType.COMMA,
        }
        if c in single_ops:
            self.tokens.append(Token(single_ops[c], c, self.line, start_col))
            self.column += 1
        else:
            self._add_error(f"Carácter no reconocido: '{c}'", start_col)

    # --- errores ---
    def _add_error(self, message: str, column: int):
        self.errors.append(LexError(self.line, column, message))

    
    def _propagate_type_declaration(self):
        temp_pos = self.pos
        temp_line = self.line
        temp_col = self.column

        while self._peek() in " \t\r\n":
            if self._peek() == "\n":
                temp_line += 1; temp_col = 1
            else:
                temp_col += 1
            self.pos += 1

        # tipo
        start_tipo = self.pos
        while self._peek().isalpha():
            self._advance()
        tipo = self.source[start_tipo:self.pos]

        while self._peek() in " \t":
            self._advance()

        # id
        start_id = self.pos
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()
        identificador = self.source[start_id:self.pos]

        if tipo and identificador:
            if self.current_function:
                self.symbols.add_local(self.current_function, identificador, tipo)
            else:
                self.symbols.add_if_absent(identificador, temp_line, tipo)
                self.symbols.update_type(identificador, tipo)

        self.pos = temp_pos

    
    def _capture_value_assignment(self, start_col):
        
        left = self.pos - 2
        while left >= 0 and (self.source[left].isalnum() or self.source[left] == "_"):
            left -= 1
        ident = self.source[left + 1:self.pos - 1].strip()

        
        temp_pos = self.pos
        while self._peek() in " \t":
            self._advance()
        start_val = self.pos
        
        while not self._is_at_end() and self._peek() not in ";\n":
            self._advance()
        valor = self.source[start_val:self.pos].strip()

        if ident and valor:
            
            val = valor.strip()
            if len(val) >= 2 and val[0] == "'" and val[-1] == "'":
                val = val[1:-1]
            self.symbols.update_value(ident, val)

        
        self.pos = temp_pos

    def _propagate_function_declaration(self):
        temp_pos = self.pos
        temp_line = self.line
        temp_col = self.column

        # espacios
        while self._peek() in " \t\r\n":
            if self._peek() == "\n":
                temp_line += 1; temp_col = 1
            else:
                temp_col += 1
            self.pos += 1

        # tipo de retorno
        start_tipo = self.pos
        while self._peek().isalpha():
            self._advance()
        ret_type = self.source[start_tipo:self.pos].strip()
        if not ret_type:
            self.pos = temp_pos
            return

        # espacios
        while self._peek() in " \t\r\n":
            self.pos += 1

        # nombre de función
        if not (self._peek().isalpha() or self._peek() == "_"):
            self.pos = temp_pos
            return
        start_name = self.pos
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()
        func_name = self.source[start_name:self.pos]

        # espacios
        while self._peek() in " \t\r\n":
            self.pos += 1

        # '('
        if self._peek() != "(":
            self.pos = temp_pos
            return
        self._advance()

        # parámetros
        param_types = []
        param_names = []
        while not self._is_at_end():
            while self._peek() in " \t\r\n":
                self.pos += 1
            if self._peek() == ")":
                self._advance()
                break

            # tipo del parámetro
            start_ptype = self.pos
            while self._peek().isalpha():
                self._advance()
            ptype = self.source[start_ptype:self.pos].strip()
            if not ptype:
                break

            while self._peek() in " \t":
                self._advance()

            # nombre del parámetro
            if not (self._peek().isalpha() or self._peek() == "_"):
                break
            start_pid = self.pos
            while self._peek().isalnum() or self._peek() == "_":
                self._advance()
            pid = self.source[start_pid:self.pos]

            # registrar en local
            self.symbols.add_local(func_name, pid, ptype)
            param_types.append(ptype)
            param_names.append(pid)

            while self._peek() in " \t\r\n":
                self.pos += 1
            if self._peek() == ",":
                self._advance()
                continue
            elif self._peek() == ")":
                self._advance()
                break
            else:
                break

        
        try:
            self.symbols.declare_function(func_name, ret_type or "void", param_types)
        except AttributeError:
            self.pos = temp_pos
            return

        self._awaiting_function_body_of = func_name
        self._pending_param_names = set(param_names)

       
        self.pos = temp_pos
