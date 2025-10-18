from .symbol_entry import SymbolEntry

class SymbolTable:
    """Gestiona la tabla de símbolos global (y locales si las hubiera)."""
    def __init__(self):
        self._symbols = {}

    def add_if_absent(self, name: str, line: int) -> SymbolEntry:
        """Añade un símbolo si no existe y devuelve la entrada."""
        if name not in self._symbols:
            entry = SymbolEntry(name=name, first_line=line)
            self._symbols[name] = entry
        return self._symbols[name]

    def update_type(self, name: str, type_: str):
        """Actualiza el tipo de un símbolo existente."""
        if name in self._symbols:
            self._symbols[name].type = type_

    def update_value(self, name: str, value: str):
        """Actualiza el valor de un símbolo existente."""
        if name in self._symbols:
            self._symbols[name].value = value

    def lookup(self, name: str) -> SymbolEntry:
        """Devuelve el símbolo o None si no existe."""
        return self._symbols.get(name)

    def dump(self) -> str:
        """Devuelve una cadena formateada con toda la tabla."""
        result = ["NOMBRE          TIPO       AMBITO     VALOR        LINEA"]
        result.append("-" * 65)
        for entry in self._symbols.values():
            result.append(entry.to_row())
        return "\n".join(result)

