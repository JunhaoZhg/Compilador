import os
from an_lexico import Lexer
from an_sintactico import Parser
from Tabla_Simbolos.symbol_table import SymbolTable
from Tabla_Simbolos.symbol_entry import SymbolEntry

def procesar_archivo(filepath):
    nombre_archivo = os.path.basename(filepath)
    nombre_sin_ext, _ = os.path.splitext(nombre_archivo)
    
    dir_padre = os.path.dirname(filepath) 
   
    output_dir = os.path.join(dir_padre, nombre_sin_ext)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Leer código fuente
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    # 1. Análisis Léxico
    SymbolEntry.reset_contador()
    symbols = SymbolTable()
    lexer = Lexer(source, symbols)
    tokens, lex_errors = lexer.tokenize()

    # --- Salidas Léxico ---
    tokens_path = os.path.join(output_dir, f"resultado_tokens_{nombre_sin_ext}.txt")
    symbols_path = os.path.join(output_dir, f"resultado_symbols_{nombre_sin_ext}.txt")
    errors_path = os.path.join(output_dir, f"resultado_errors_{nombre_sin_ext}.txt")

    with open(tokens_path, "w", encoding="utf-8") as ft:
        for t in tokens:
            ft.write(str(t) + "\n")
    
    with open(symbols_path, "w", encoding="utf-8") as fs:
        fs.write(symbols.dump())

    # 2. Análisis Sintáctico 
    parse_path = os.path.join(output_dir, f"resultado_parse_{nombre_sin_ext}.txt")
    syn_errors = []

    if not lex_errors:
        # Instanciamos el Parser pasándole los tokens limpios
        parser = Parser(tokens)
        rules_applied, syn_errors = parser.parse()

        # Guardar reglas (Parse) para VASt
        with open(parse_path, "w", encoding="utf-8") as fp:
            linea_reglas = " ".join(str(r) for r in rules_applied)
            fp.write(f"Descendente {linea_reglas}")
            
    else:
        with open(parse_path, "w", encoding="utf-8") as fp:
            fp.write("No se realizó análisis sintáctico debido a errores léxicos.")

    # 3. Errores Totales
    with open(errors_path, "w", encoding="utf-8") as fe:
        if lex_errors or syn_errors:
            for e in lex_errors:
                fe.write(str(e) + "\n")
            for e in syn_errors:
                fe.write(str(e) + "\n")
        else:
            fe.write("No se detectaron errores.\n")

    print(f"Analizado: {nombre_archivo}")
    print(f"   → Tokens: {tokens_path}")
    print(f"   → Parse:  {parse_path}")
    print("-" * 70)


def main():
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    pruebas_dir = os.path.join(base_dir, "pruebas")
    
    extensiones_validas = (".myjs", ".txt", ".javascript")

    if not os.path.exists(pruebas_dir):
        print(f"No se encontró el directorio de pruebas: {pruebas_dir}")
        return

    archivos = []
    
    for nombre_archivo in os.listdir(pruebas_dir):
        ruta_completa = os.path.join(pruebas_dir, nombre_archivo)
       
        if os.path.isfile(ruta_completa) and nombre_archivo.lower().endswith(extensiones_validas):
            archivos.append(ruta_completa)

    if not archivos:
        print(f"No se encontraron archivos de entrada (.myjs, .txt o .javascript) en {pruebas_dir}.")
        return

    print(f"Se encontraron {len(archivos)} archivo(s) para analizar en '{pruebas_dir}':\n")
    for a in archivos:
        print(f" - {os.path.basename(a)}")

    print("\nIniciando análisis...\n" + "=" * 70)

    for archivo in archivos:
        procesar_archivo(archivo)

    print("Análisis completado.\n")


if __name__ == "__main__":
    main()

