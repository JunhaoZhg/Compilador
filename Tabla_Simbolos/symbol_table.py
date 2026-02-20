from Tabla_Simbolos.symbol_entry import SymbolEntry

TYPE_SIZE = {
    "int": 2,
    "boolean": 2,
    "float": 4,
    "string": 128,
    "void": 0,
    "id": 2,  
    "-": 0,
}

class SymbolTable:
    def __init__(self, nombre_ambito="global"):
        self.nombre_ambito = nombre_ambito
        self.simbolos = {}
        self.desplazamiento_actual = 0
        self.locales = {}  

    
    def _alloc_offset(self, tipo: str) -> int:
        sz = TYPE_SIZE.get(tipo, 2)
        off = self.desplazamiento_actual
        self.desplazamiento_actual += sz
        return off

    # ---------- global / local ----------
    def insertar(self, simbolo: SymbolEntry):
        if simbolo.lexema in self.simbolos:
            raise ValueError(f"Símbolo '{simbolo.lexema}' ya declarado en ámbito {self.nombre_ambito}")
        if simbolo.desplazamiento is None and TYPE_SIZE.get(simbolo.tipo, 0) > 0 and simbolo.categoria != "Función":
            simbolo.desplazamiento = self._alloc_offset(simbolo.tipo)
        self.simbolos[simbolo.lexema] = simbolo

    def buscar(self, lexema: str):
        return self.simbolos.get(lexema)

    def add_if_absent(self, lexema, linea, tipo="id", desplazamiento=None, categoria="Variable"):
        ent = self.simbolos.get(lexema)
        if ent is None:
            if categoria == "Función":
                ent = SymbolEntry("Función", lexema, tipo or "void", desplazamiento=None)
            else:
                t = tipo if tipo != "id" else "int"
                off = desplazamiento
                if off is None and TYPE_SIZE.get(t, 0) > 0:
                    off = self._alloc_offset(t)
                ent = SymbolEntry("Variable", lexema, t, off)
            self.simbolos[lexema] = ent
        return ent

    def update_type(self, lexema, tipo):
        ent = self.simbolos.get(lexema)
        if not ent:
            return
        ent.tipo = tipo
        if ent.categoria != "Función" and ent.desplazamiento is None and TYPE_SIZE.get(tipo, 0) > 0:
            ent.desplazamiento = self._alloc_offset(tipo)

    def update_value(self, lexema, valor):
       
        return

    # ---------- funciones y locales ----------
    def declare_function(self, nombre_funcion, tipo_retorno="void", tipos_params=None):
        tipos_params = tipos_params or []
        entry = self.add_if_absent(nombre_funcion, 0, tipo_retorno, categoria="Función")
        entry.num_params = len(tipos_params)
        entry.tipos_params = tipos_params
        if nombre_funcion not in self.locales:
            self.locales[nombre_funcion] = SymbolTable(nombre_funcion)

    def add_local(self, nombre_funcion, lexema, tipo="id"):
        if nombre_funcion not in self.locales:
            self.locales[nombre_funcion] = SymbolTable(nombre_funcion)
        self.locales[nombre_funcion].add_if_absent(lexema, 0, tipo, categoria="Variable")

    # ---------- salida ----------
    def __str__(self):
        cabecera = (
            f"=== TABLA DE SÍMBOLOS LOCAL DE {self.nombre_ambito} ==="
            if self.nombre_ambito != "global"
            else "=== TABLA DE SÍMBOLOS GLOBAL ==="
        )
        salida = [cabecera, "===== TABLA DE SÍMBOLOS ====="]
        for s in self.simbolos.values():
            salida.append(str(s))
        salida.append("=============================")
        if self.nombre_ambito == "global":
            for tabla in self.locales.values():
                salida.append("")
                salida.append(str(tabla))
        return "\n".join(salida)

    def dump(self):
        return str(self)
