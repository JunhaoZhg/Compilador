from enum import Enum, auto

class TokenType(Enum):
    # Especiales
    EOF = auto()

    # Identificadores y literales
    ID = auto()
    INT_CONST = auto()
    FLOAT_CONST = auto()
    STRING_CONST = auto()

    # Palabras clave
    LET = auto()
    INT = auto()
    FLOAT = auto()
    BOOLEAN = auto()
    STRING = auto()
    VOID = auto()
    FUNCTION = auto()
    RETURN = auto()
    IF = auto()
    ELSE = auto()
    DO = auto()
    WHILE = auto()
    READ = auto()
    WRITE = auto()
    TRUE = auto()
    FALSE = auto()

    # Nuestros operadores 
    PLUS = auto()          # +
    LT = auto()            # <
    NOT = auto()           # !
    ASSIGN = auto()        # =
    OR_ASSIGN = auto()     # |=

    # Puntuación
    LPAREN = auto()        # (
    RPAREN = auto()        # )
    LBRACE = auto()        # {
    RBRACE = auto()        # }
    SEMICOLON = auto()     # ;
    COMMA = auto()         # ,
