from Tabla_Simbolos.symbol_table import SymbolTable
from Tabla_Simbolos.symbol_entry import SymbolEntry

class GestorTablas:
    

    def __init__(self):
        self.tabla_global = SymbolTable("global")
        self.locales = {}

    # -------- Registro de variables o funciones --------
    def registrar_variable_global(self, lexema, tipo="id"):
        self.tabla_global.add_if_absent(lexema, 0, tipo, categoria="Variable")

    def registrar_funcion(self, nombre_funcion, tipo="void"):
       
        self.tabla_global.add_if_absent(nombre_funcion, 0, tipo, categoria="Función")
        if nombre_funcion not in self.locales:
            self.locales[nombre_funcion] = SymbolTable(nombre_funcion)

    def registrar_variable_local(self, nombre_funcion, lexema, tipo="id"):
        if nombre_funcion not in self.locales:
            self.locales[nombre_funcion] = SymbolTable(nombre_funcion)
        self.locales[nombre_funcion].add_if_absent(lexema, 0, tipo, categoria="Variable")

    # -------- Salida --------
    def __str__(self):
        salida = [str(self.tabla_global)]
        for tabla in self.locales.values():
            salida.append(str(tabla))
        return "\n\n".join(salida)

    def dump(self):
        return str(self)


