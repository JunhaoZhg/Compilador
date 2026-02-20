class SymbolEntry:
    _contador_indices = 0

    @classmethod
    def reset_contador(cls):
        
        cls._contador_indices = 0
    # ------------------------------------------------------------------------

    def __init__(self, categoria, lexema, tipo="-", desplazamiento=None, valor=None, num_params=0, tipos_params=None):
        self.index = SymbolEntry._contador_indices
        SymbolEntry._contador_indices += 1
        # --------------------------------------------------

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
        prefix = f"({self.index})" 
        # ----------------------------------------------------------

        if self.categoria == "Función":
            tipos_str = "[" + ", ".join(self.tipos_params) + "]"
            return f"{prefix} [{self.categoria}] lexema='{self.lexema}', tipo='{self.tipo}', Nºparams={self.num_params}, tipos={tipos_str}"
        else:
            tipo = self.tipo or "-"
            off = self.desplazamiento if self.desplazamiento is not None else "-"
            return f"{prefix} [{self.categoria}] lexema='{self.lexema}', tipo='{tipo}', desplazamiento={off}"
