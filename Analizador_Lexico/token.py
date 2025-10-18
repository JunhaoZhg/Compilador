from dataclasses import dataclass
from .token_types import TokenType

@dataclass
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int
    # Para IDs puedes guardar aquí la posición/índice de la TS 
    attribute: str = ""

    def __str__(self) -> str:
        """
        Formato oficial de salida:
            <codigo, atributo>
        """
        code = self._code()
        attr = self._attr()
        return f"<{code}, {attr}>" if attr else f"<{code}, >"

    # ---------- Código (nombre del token) en el fichero ----------
    def _code(self) -> str:
        """
        Mapea todos los TokenType al 'codigo' que se vuelca en tokens.txt.
        """
        codes = {
            # Especiales
            TokenType.EOF:           "EOF",

            # Identificadores y literales
            TokenType.ID:            "ID",      # identificador
            TokenType.INT_CONST:     "ENT",     # entero
            TokenType.FLOAT_CONST:   "REAL",    # real
            TokenType.STRING_CONST:  "CAD",     # cadena

            # Palabras reservadas
            TokenType.LET:       "LET",
            TokenType.INT:       "INT",
            TokenType.FLOAT:     "FLOAT",
            TokenType.BOOLEAN:   "BOOLEAN",
            TokenType.STRING:    "STRING",
            TokenType.VOID:      "VOID",
            TokenType.FUNCTION:  "FUNCTION",
            TokenType.RETURN:    "RETURN",
            TokenType.IF:        "IF",
            TokenType.ELSE:      "ELSE",
            TokenType.DO:        "DO",
            TokenType.WHILE:     "WHILE",
            TokenType.READ:      "READ",
            TokenType.WRITE:     "WRITE",
            TokenType.TRUE:      "TRUE",
            TokenType.FALSE:     "FALSE",

            # Operadores 
            TokenType.PLUS:      "SUMA",      # +
            TokenType.LT:        "MENOR",     # <
            TokenType.NOT:       "DIST",      # !  
            TokenType.ASSIGN:    "ASSIG",     # =
            TokenType.OR_ASSIGN: "ORASSIG",  # |=  

            # Delimitadores 
            TokenType.LPAREN:    "LPAR",      # (
            TokenType.RPAREN:    "RPAR",      # )
            TokenType.LBRACE:    "LLAVEI",    # {  
            TokenType.RBRACE:    "LLAVED",    # }   
            TokenType.SEMICOLON: "PCOMA",     # ;
            TokenType.COMMA:     "COMA",      # ,
        }
        return codes.get(self.type, self.type.name)

    # ---------- Atributo (valor) en el fichero ----------
    def _attr(self) -> str:
        """
        Atributo del token según su tipo:
        - ID: se usa 'attribute' si viene. Si no, el lexema.
        - INT/FLOAT: el lexema tal cual.
        - CADENA: se imprime entre comillas dobles.
        - Otros: atributo vacío.
        """
        t = self.type

        if t == TokenType.ID:
            return (self.attribute or self.lexeme)

        if t in (TokenType.INT_CONST, TokenType.FLOAT_CONST):
            return self.lexeme

        if t == TokenType.STRING_CONST:
            # En el fuente usas comillas simples; en tokens.txt deben ir con comillas dobles.
            # Quitamos comillas simples exteriores si vienen en el lexema y envolvemos en dobles.
            raw = self.lexeme
            if len(raw) >= 2 and raw[0] == "'" and raw[-1] == "'":
                contenido = raw[1:-1]
            else:
                contenido = raw
            # Escapar comillas dobles internas si las hubiera
            contenido = contenido.replace('"', '\\"')
            return f"\"{contenido}\""

        # Para palabras clave, operadores y delimitadores normalmente no se pone atributo
        return ""
