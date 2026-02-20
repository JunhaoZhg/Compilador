from dataclasses import dataclass
from token_types import TokenType

@dataclass
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int
    
    attribute: str = ""

    def __str__(self) -> str:
        
        code = self._code()
        attr = self._attr()
        return f"<{code}, {attr}>" if attr else f"<{code}, >"

    
    def _code(self) -> str:
       
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

    
    def _attr(self) -> str:

        t = self.type

        if t == TokenType.ID:
            return (self.attribute or self.lexeme)

        if t in (TokenType.INT_CONST, TokenType.FLOAT_CONST):
            return self.lexeme

        if t == TokenType.STRING_CONST:
           
            raw = self.lexeme
            if len(raw) >= 2 and raw[0] == "'" and raw[-1] == "'":
                contenido = raw[1:-1]
            else:
                contenido = raw
            
            contenido = contenido.replace('"', '\\"')
            return f"\"{contenido}\""

        
        return ""
