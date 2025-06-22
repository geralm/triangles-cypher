# -*- coding: utf-8 -*-
import argparse
import json
import matplotlib.pyplot as plt
import unicodedata

SCREEN_WITH=1200
SCREEN_HEIGHT=800

MARGIN_LEFT=10
MARGIN_RIGHT=10

INITIAL_BASELINE=750 #position in y axis 

# Definición de LINES_MAP base
LINES_MAP = {
    "bottom_left":    [10, 30, 20, 15],
    "bottom_right":   [30, 30, 20, 15],
    "center":         [10, 30, 30, 30],
    "top_left":       [10, 30, 20, 45],
    "top_right":      [30, 30, 20, 45],
}
def remove_accent(text):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', text)
        if not unicodedata.combining(c)
    )

# Cargar keymap (abecedario)
def load_keymap(keymap_file="keymap.json"):
    """Carga el archivo keymap_file y lo devuelve como un diccionario."""
    try:
        with open(keymap_file, "r") as file:
            keymap = json.load(file)
        return keymap
    except FileNotFoundError:
        print(f"El archivo {keymap_file} no se encuentra.")
        raise
    except json.JSONDecodeError:
        print(f"Error al decodificar {keymap_file}.")
        raise

# Leer archivo de texto
def read_file_content(input_file):
    """Lee el contenido de un archivo de texto y lo devuelve como una lista de líneas."""
    try:
        with open(input_file, "r") as file:
            content = file.readlines()
        return content
    except FileNotFoundError:
        print(f"El archivo {input_file} no se encuentra.")
        raise
    except Exception as e:
        print(f"Error al leer el archivo {input_file}: {e}")
        raise

# Dibuja una letra
def draw_letter(ax, letter_config, position, size):
    """
    Dibuja una letra en la posición (x, baseline_y), con el tamaño especificado.
    """
    x_offset, baseline_y = position
    scale = size / 50  # Escala base

    for line_key in letter_config:
        if line_key and line_key in LINES_MAP:
            x1, y1, x2, y2 = LINES_MAP[line_key]

            # X normal
            x1 = x_offset + x1 * scale
            x2 = x_offset + x2 * scale

            # Y invertido: baseline abajo
            y1 = baseline_y - (y1 * scale)
            y2 = baseline_y - (y2 * scale)

            ax.plot([x1, x2], [y1, y2], color='black', linewidth=2)
        else:
            print(f"Advertencia: línea '{line_key}' no existe en LINES_MAP")

def check_fit(word, x_pos, letter_box_spacing):
    """
    Verifica si la palabra cabe en la línea actual.
    Retorna True si cabe, False si no.
    """
    word_width = len(word) * letter_box_spacing
    return (x_pos + word_width) <= (SCREEN_WITH - MARGIN_RIGHT)



def draw_text(ax, keymap, input_content, size):
    """
    Dibuja todo el texto leído en el canvas, sin padding/margen entre letras,
    respetando altura de renglón.
    """
    letter_box_width = size * 0.4   #0.4 tamaño de caja por letra (ajustable)
    line_height = size * 0.6  # 0.6 altura de renglón proporcional

    margin_left = MARGIN_LEFT
    baseline_y = INITIAL_BASELINE  # baseline inicial

    x_pos = margin_left

    for line in input_content:
        text_line = line.strip('\n')
        text_line = remove_accent(text_line)

        if not text_line:
            # salto de línea
            baseline_y -= line_height
            x_pos = margin_left
            continue

        words = text_line.split(" ")
        for word in words:
            #check if the word fits in the same line
            word_fits = check_fit(word , x_pos, letter_box_width)
            if not word_fits:
                baseline_y -= line_height
                x_pos = margin_left

            for letter in word:
                if letter.lower() in keymap:
                    draw_letter(ax, keymap[letter.lower()], (x_pos, baseline_y), size)
                    x_pos += letter_box_width
                elif letter == " ":
                    x_pos += letter_box_width               
                else:
                    print(f"Letra no encontrada en keymap: '{letter}'")

        # Al terminar la línea → salto de línea
        baseline_y -= line_height
        x_pos = margin_left

# Main program
def main():
    parser = argparse.ArgumentParser(description="Genera un PDF o imagen con texto dibujado en líneas.")

    parser.add_argument("-o", required=True, type=str, help="Nombre del archivo de salida (PDF o PNG).")
    parser.add_argument("-i", required=True, type=str, help="Archivo de texto con el contenido a traducir.")
    parser.add_argument("--shuffle", action="store_true", help="Indica si se debe mezclar el contenido. (no implementado)")
    parser.add_argument("--dotted-guidelines", action="store_true", help="Indica si se deben dibujar las líneas guía con estilo punteado.")
    parser.add_argument("--no-abc", action="store_true", help="Indica si NO se debe generar el archivo abecedario {filename}_abc.pdf")
    parser.add_argument("--no-decoded", action="store_true", help="Indica si NO se debe generar el archivo {filename}_decoded.pdf")
    parser.add_argument("--size", type=int, default=50, help="Tamaño de la letra. Por defecto es 50.")
    parser.add_argument("--letter-spacing", type=int, default=0.4, help="Espacio entre letras")
    parser.add_argument("--line-spacing", type=int, default=0.6, help="Espacio entre lineas")
    parser.add_argument("--keymapfile", type=str, default="keymap.json", help="Archivo keymap a cargar (default: keymap.json).")

    args = parser.parse_args()

    # Cargar keymap
    try:
        keymap = load_keymap(args.keymapfile)
        print("Keymap cargado correctamente.")
    except Exception as e:
        print(f"Error al cargar el keymap: {e}")
        return

    # Leer contenido del archivo de texto
    try:
        input_content = read_file_content(args.i)
        print("Contenido leído:", input_content)
    except Exception as e:
        print(f"Error al leer el archivo de texto: {e}")
        return

    # Crear canvas
    fig, ax = plt.subplots(figsize=(12, 8))

    # Dibujar el texto
    draw_text(ax, keymap, input_content, args.size)

    # Ajustes finales del canvas
    ax.set_xlim(0, SCREEN_WITH)
    ax.set_ylim(0, SCREEN_HEIGHT)
    ax.axis('off')

    # Guardar el resultado
    try:
        output_filename = args.o
        if output_filename.lower().endswith(".pdf") or output_filename.lower().endswith(".png"):
            plt.savefig(output_filename, bbox_inches='tight', dpi=300)
            print(f"Archivo generado exitosamente: {output_filename}")
        else:
            print("Error: el archivo de salida debe tener extensión .pdf o .png")
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")

if __name__ == "__main__":
    main()
