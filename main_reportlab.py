# main.py

# -*- coding: utf-8 -*-
import argparse
from SymbolicEncoderReportLab import SymbolicEncoder

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
        print(f"Error al leer el archivo de texto: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Genera un PDF con texto cifrado utilizando ReportLab.")

    parser.add_argument("-o", required=True, type=str, help="Nombre base del archivo de salida (sin extensión).")
    parser.add_argument("-i", required=True, type=str, help="Archivo de texto con el contenido a cifrar.")
    parser.add_argument("--no-abc", action="store_true", help="Indica si NO se debe generar el abecedario.")
    parser.add_argument("--no-decoded", action="store_true", help="Indica si NO se debe generar la versión con letras debajo.")
    parser.add_argument("--size", type=int, default=50, help="Tamaño de la letra. Por defecto es 50.")
    parser.add_argument("--letter-spacing", type=float, default=0.4, help="Espacio entre letras.")
    parser.add_argument("--line-spacing", type=float, default=0.6, help="Espacio entre líneas.")
    parser.add_argument("--keymapfile", type=str, default="keymap.json", help="Archivo keymap a cargar (default: keymap.json).")

    args = parser.parse_args()

    try:
        input_content = read_file_content(args.i)
    except Exception as e:
        print(f"Error al leer el archivo de texto: {e}")
        return

    encoder = SymbolicEncoder(
        keymap_file=args.keymapfile,
        size=args.size
    )

    # Generar abecedario
    if not args.no_abc:
        print("Generando abecedario...")
        encoder.generate_abc(
            output_filename=f"{args.o}_abc.pdf",
            letter_spacing=args.letter_spacing,
            line_spacing=args.line_spacing
        )

    # Generar texto con solución (letras debajo)
    if not args.no_decoded:
        print("Generando texto con letras debajo...")
        encoder.generate_text_solution(
            input_content,
            output_filename=f"{args.o}_decoded.pdf",
            letter_spacing=args.letter_spacing,
            line_spacing=args.line_spacing
        )

    # Generar texto codificado puro
    print("Generando texto cifrado puro...")
    encoder.generate_text_encoded(
        input_content,
        output_filename=f"{args.o}.pdf",
        letter_spacing=args.letter_spacing,
        line_spacing=args.line_spacing
    )

if __name__ == "__main__":
    main()
