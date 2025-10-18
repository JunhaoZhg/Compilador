class LexError:
    """Representa un error léxico detectado por el analizador."""

    def __init__(self, line: int, column: int, message: str):
        self.line = line
        self.column = column
        self.message = message

    def __str__(self) -> str:
        return f"[LÉXICO] Línea {self.line}, Columna {self.column}: {self.message}"
