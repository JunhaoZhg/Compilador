import os
from Analizador_Lexico.an_lexico import Lexer
from Tabla_Simbolos.symbol_table import SymbolTable



def procesar_archivo(filepath):
    nombre_archivo = os.path.basename(filepath)
    nombre_sin_ext, _ = os.path.splitext(nombre_archivo)
    base_dir = os.path.dirname(filepath)

    # Leer código fuente
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    # Inicializar tabla de símbolos y analizador léxico
    symbols = SymbolTable()
    lexer = Lexer(source, symbols)

    # Ejecutar análisis léxico
    tokens, errors = lexer.tokenize()

    # --- Ficheros de salida ---
    tokens_path = os.path.join(base_dir, f"resultado_tokens_{nombre_sin_ext}.txt")
    symbols_path = os.path.join(base_dir, f"resultado_symbols_{nombre_sin_ext}.txt")
    errors_path = os.path.join(base_dir, f"resultado_errors_{nombre_sin_ext}.txt")

    # Volcar resultados
    with open(tokens_path, "w", encoding="utf-8") as ft:
        for t in tokens:
            ft.write(str(t) + "\n")

    with open(symbols_path, "w", encoding="utf-8") as fs:
        fs.write(symbols.dump())

    with open(errors_path, "w", encoding="utf-8") as fe:
        if errors:
            for e in errors:
                fe.write(str(e) + "\n")
        else:
            fe.write("No se detectaron errores léxicos.\n")

    print(f"Analizado: {nombre_archivo}")
    print(f"   → {tokens_path}")
    print(f"   → {symbols_path}")
    print(f"   → {errors_path}")
    print("-" * 70)


def main():
    """Busca y analiza todos los archivos fuente (.myjs, .txt, .javascript) en este directorio y subcarpetas."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    extensiones_validas = (".myjs", ".txt", ".javascript")

    archivos = []
    for root, _, files in os.walk(current_dir):
        for file in files:
            if file.lower().endswith(extensiones_validas):
                archivos.append(os.path.join(root, file))

    if not archivos:
        print("No se encontraron archivos de entrada (.myjs, .txt o .javascript).")
        return

    print(f"Se encontraron {len(archivos)} archivo(s) para analizar:\n")
    for a in archivos:
        print(f" - {os.path.relpath(a, current_dir)}")

    print("\nIniciando análisis...\n" + "=" * 70)

    for archivo in archivos:
        procesar_archivo(archivo)

    print("Análisis completado.\n")


if __name__ == "__main__":
    main()

