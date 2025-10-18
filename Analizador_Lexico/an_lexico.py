from .token import Token
from .token_types import TokenType
from .errors import LexError

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

    # ---------------- Tokenización general ----------------
    def tokenize(self):
        """Analiza el texto fuente y genera tokens."""
        while not self._is_at_end():
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

        # Al final del archivo
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
        # salto de línea se maneja fuera
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
            entry = self.symbols.add_if_absent(lexeme, self.line)
            token = Token(ttype, lexeme, self.line, start_col, attribute=entry.name)
        else:
            token = Token(ttype, lexeme, self.line, start_col)
        self.tokens.append(token)
        self.column += len(lexeme)

        if ttype == TokenType.LET:
            self._propagate_type_declaration()

    # --- números ---
    def _number(self, first_char):
        start_pos = self.pos - 1
        start_col = self.column
        while self._peek().isdigit():
            self._advance()

        if self._peek() == ".":
            self._advance()
            if not self._peek().isdigit():
                self._add_error("Número real mal formado (falta dígito tras '.')", start_col)
                return
            while self._peek().isdigit():
                self._advance()
            lexeme = self.source[start_pos:self.pos]
            token = Token(TokenType.FLOAT_CONST, lexeme, self.line, start_col)
        else:
            lexeme = self.source[start_pos:self.pos]
            token = Token(TokenType.INT_CONST, lexeme, self.line, start_col)

        self.tokens.append(token)
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
        self._advance()  # cerrar comilla
        lexeme = self.source[start_pos - 1:self.pos]
        self.tokens.append(Token(TokenType.STRING_CONST, lexeme, self.line, start_col))
        self.column += len(lexeme)

    # --- operadores / delimitadores ---
    def _operator_or_punctuator(self, c):
        start_col = self.column
        # operadores de dos caracteres (|=)
        if c == "|" and self._peek() == "=":
            self._advance()
            self.tokens.append(Token(TokenType.OR_ASSIGN, "|=", self.line, start_col))
            self.column += 2
            return

        # operadores simples
        single_ops = {
            "+": TokenType.PLUS,
            "<": TokenType.LT,
            "!": TokenType.NOT,
            "=": TokenType.ASSIGN,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "{": TokenType.LBRACE,
            "}": TokenType.RBRACE,
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


    # ------detectar tipo en declaraciones "let <tipo> <id>;"-------
    def _propagate_type_declaration(self):
        """Detecta 'let <tipo> <id>' y asigna el tipo al símbolo."""
        temp_pos = self.pos
        temp_line = self.line
        temp_col = self.column

        # Saltar espacios
        while self._peek() in " \t\r\n":
            if self._peek() == "\n":
                temp_line += 1
                temp_col = 1
            else:
                temp_col += 1
            self.pos += 1

        # Leer tipo
        start_tipo = self.pos
        while self._peek().isalpha():
            self._advance()
        tipo = self.source[start_tipo:self.pos]

        # Saltar espacios
        while self._peek() in " \t":
            self._advance()

        # Leer identificador
        start_id = self.pos
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()
        identificador = self.source[start_id:self.pos]

        if tipo and identificador:
            self.symbols.add_if_absent(identificador, temp_line)
            self.symbols.update_type(identificador, tipo)

        self.pos = temp_pos

    # ---------- detectar asignaciones "<id> = <valor>;"-------------------
    def _capture_value_assignment(self, start_col):
        """Detecta una asignación simple y guarda el valor en la tabla de símbolos."""
        # Retroceder para encontrar el identificador a la izquierda del '='
        left = self.pos - 2
        while left >= 0 and (self.source[left].isalnum() or self.source[left] == "_"):
            left -= 1
        ident = self.source[left + 1:self.pos - 1].strip()

        # Avanzar para leer el valor
        temp_pos = self.pos
        while self._peek() in " \t":
            self._advance()
        start_val = self.pos
        # Leer hasta ; o salto de línea
        while not self._is_at_end() and self._peek() not in ";\n":
            self._advance()
        valor = self.source[start_val:self.pos].strip()

        if ident and valor:
            # Limpiar valor: quitar comillas si es cadena
            val = valor.strip()
            if len(val) >= 2 and val[0] == "'" and val[-1] == "'":
                val = val[1:-1]
            self.symbols.update_value(ident, val)

        # Restaurar posición del lexer
        self.pos = temp_pos