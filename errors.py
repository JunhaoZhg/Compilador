class LexError:
    

    def __init__(self, line: int, column: int, message: str):
        self.line = line
        self.column = column
        self.message = message

    def __str__(self) -> str:
        return f"ERROR LÉXICO (Línea {self.line}, Columna {self.column}): {self.message}"


class SyntacticError:
   

    def __init__(self, line: int, column: int, message: str):
        self.line = line
        self.column = column
        self.message = message

    def __str__(self) -> str:
        return f"ERROR SINTÁCTICO (Línea {self.line}, Columna {self.column}): {self.message}"
    
class SemanticError:
    

    def __init__(self, line: int, column: int, message: str):
        self.line = line
        self.column = column
        self.message = message

    def __str__(self) -> str:
        return f"ERROR SEMÁNTICO (Línea {self.line}, Columna {self.column}): {self.message}"
