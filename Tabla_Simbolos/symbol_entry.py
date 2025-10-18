from dataclasses import dataclass

@dataclass
class SymbolEntry:
    """Representa una entrada en la tabla de símbolos."""
    name: str
    type: str = "-"
    scope: str = "global"
    value: str = "-"
    first_line: int = 0

    def to_row(self) -> str:
        """Devuelve una línea formateada para el volcado."""
        return f"{self.name:<15} {self.type:<10} {self.scope:<10} {self.value:<10} (línea {self.first_line})"
