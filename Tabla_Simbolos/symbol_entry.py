class SymbolEntry:
    def __init__(self, categoria, lexema, tipo="-", desplazamiento=None, valor=None, num_params=0, tipos_params=None):
        self.categoria = categoria
        self.lexema = lexema
        self.tipo = tipo
        self.desplazamiento = desplazamiento
        self.num_params = num_params
        self.tipos_params = tipos_params or []

    @property
    def name(self):
        return self.lexema

    def __str__(self):
        if self.categoria == "Función":
            tipos_str = "[" + ", ".join(self.tipos_params) + "]"
            return f"[{self.categoria}] lexema='{self.lexema}', tipo='{self.tipo}', Nºparams={self.num_params}, tipos={tipos_str}"
        else:
            tipo = self.tipo or "-"
            off = self.desplazamiento if self.desplazamiento is not None else "-"
            return f"[{self.categoria}] lexema='{self.lexema}', tipo='{tipo}', desplazamiento={off}"
