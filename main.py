# main.py

# -*- coding: utf-8 -*-
import argparse
from SymbolicEncoder import SymbolicEncoder

def read_file_content(input_file):
    """Lee el contenido de un archivo de texto y lo devuelve como una lista de líneas."""
    try:
        with open(input_file, "r") as file:
            content = file.readlines()
        print("Contenido leído:", content)
        return content
    except FileNotFoundError:
        print(f"El archivo {input_file} no se encuentra.")
        raise
    except Exception as e:
        print(f"Error al leer el archivo {input_file}: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Genera un PDF o imagen con texto cifrado con SymbolicEncoder.")

    parser.add_argument("-o", required=True, type=str, help="Nombre base del archivo de salida (sin extensión).")
    parser.add_argument("-i", required=True, type=str, help="Archivo de texto con el contenido a cifrar.")
    parser.add_argument("--no-abc", action="store_true", help="Indica si NO se debe generar el archivo abecedario {filename}_abc.pdf")
    parser.add_argument("--no-decoded", action="store_true", help="Indica si NO se debe generar el archivo {filename}_decoded.pdf")
    parser.add_argument("--size", type=int, default=50, help="Tamaño de la letra. Por defecto es 50.")
    parser.add_argument("--letter-spacing", type=float, default=0.4, help="Espacio entre letras.")
    parser.add_argument("--line-spacing", type=float, default=0.6, help="Espacio entre líneas.")
    parser.add_argument("--keymapfile", type=str, default="keymap.json", help="Archivo keymap a cargar (default: keymap.json).")

    args = parser.parse_args()

    # Leer contenido del archivo de texto
    try:
        input_content = read_file_content(args.i)
    except Exception as e:
        print(f"Error al leer el archivo de texto: {e}")
        return

    # Crear instancia del SymbolicEncoder
    encoder = SymbolicEncoder(
        keymap_file=args.keymapfile,
        size=args.size
    )

    # Generar abecedario
    if not args.no_abc:
        print("Generando abecedario...")
        encoder.generate_abc()
        encoder.save_output(f"{args.o}_abc.pdf")

    # Generar texto cifrado + solución
    if not args.no_decoded:
        print("Generando texto con solución...")
        encoder.generate_text_solution(
            input_content,
            letter_spacing=args.letter_spacing,
            line_spacing=args.line_spacing
        )
        encoder.save_output(f"{args.o}_decoded.pdf")

    # Generar texto cifrado puro
    print("Generando texto cifrado puro...")
    encoder.generate_text_encoded(
        input_content,
        letter_spacing=args.letter_spacing,
        line_spacing=args.line_spacing
    )
    encoder.save_output(f"{args.o}.pdf")

if __name__ == "__main__":
    main()
