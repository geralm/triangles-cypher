# symbolic_encoder.py

import json
import unicodedata
import matplotlib.pyplot as plt

class SymbolicEncoder:
    # Definición de LINES_MAP base
    LINES_MAP = {
        "bottom_left":    [10, 30, 20, 15],
        "bottom_right":   [30, 30, 20, 15],
        "center":         [10, 30, 30, 30],
        "top_left":       [10, 30, 20, 45],
        "top_right":      [30, 30, 20, 45],
    }

    def __init__(self, keymap_file, size, screen_width=1200, screen_height=800, margin_left=10, margin_right=10, initial_baseline=750):
        self.fig = None
        self.ax = None

        self.keymap_file = keymap_file
        self.size = size
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.MARGIN_LEFT = margin_left
        self.MARGIN_RIGHT = margin_right
        self.INITIAL_BASELINE = initial_baseline

        self.keymap = self.load_keymap()

    @staticmethod
    def remove_accent(text):
        return ''.join(
            c for c in unicodedata.normalize('NFKD', text)
            if not unicodedata.combining(c)
        )

    def load_keymap(self):
        """Carga el archivo keymap_file y lo devuelve como un diccionario."""
        try:
            with open(self.keymap_file, "r") as file:
                keymap = json.load(file)
            print("Keymap cargado correctamente.")
            return keymap
        except FileNotFoundError:
            print(f"El archivo {self.keymap_file} no se encuentra.")
            raise
        except json.JSONDecodeError:
            print(f"Error al decodificar {self.keymap_file}.")
            raise

    def read_file_content(self, input_file):
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
    
    def draw_letter(self, ax, letter_config, position, size, show_letters=False, letter_position='below', dotted_guidelines=False, letter_char=None):
        """
        Dibuja una letra en la posición (x, baseline_y), con el tamaño especificado.
        """
        x_offset, baseline_y = position
        scale = size / 50  # Escala base

        for line_key in letter_config:
            if line_key and line_key in self.LINES_MAP:
                x1, y1, x2, y2 = self.LINES_MAP[line_key]

                x1 = x_offset + x1 * scale
                x2 = x_offset + x2 * scale
                y1 = baseline_y - (y1 * scale)
                y2 = baseline_y - (y2 * scale)

                #linestyle = (0, (3, 3)) if dotted_guidelines else 'solid'

                #ax.plot([x1, x2], [y1, y2], color='black', linewidth=2, linestyle=linestyle)
                ax.plot([x1, x2], [y1, y2], color='black', linewidth=2)
            else:
                print(f"Advertencia: línea '{line_key}' no existe en LINES_MAP")

        if show_letters and letter_char:
            if letter_position == 'below':
                ax.text(
                    x_offset + (size * 0.4),
                    baseline_y - (size * 1.2),
                    letter_char.upper(),
                    fontsize=size * 0.2,
                    ha='center'
                )
            elif letter_position == 'inside':
                ax.text(
                    x_offset + (size * 0.2),
                    baseline_y - (size * 0.5),
                    letter_char.upper(),
                    fontsize=size * 0.4,
                    ha='center'
                )

    def check_fit(self, word, x_pos, letter_box_spacing):
        """
        Verifica si la palabra cabe en la línea actual.
        Retorna True si cabe, False si no.
        """
        word_width = len(word) * letter_box_spacing
        return (x_pos + word_width) <= (self.SCREEN_WIDTH - self.MARGIN_RIGHT)

    def draw_text(self, input_content, letter_spacing=0.4, line_spacing=0.6, show_letters=False, letter_position='below', dotted_guidelines=False, trim_words=False):
        """
        Dibuja el texto completo en el canvas.
        """
        letter_box_width = self.size * letter_spacing
        line_height = self.size * line_spacing

        if show_letters and letter_position == 'below':
            # Añadimos espacio extra si las letras van abajo
            line_height += self.size * 0.3

        baseline_y = self.INITIAL_BASELINE
        x_pos = self.MARGIN_LEFT

        for line in input_content:
            text_line = line.strip('\n')
            text_line = self.remove_accent(text_line)

            if not text_line:
                baseline_y -= line_height
                x_pos = self.MARGIN_LEFT
                continue

            words = text_line.split(" ")
            for word in words:
                word_fits = self.check_fit(word, x_pos, letter_box_width)
                if not word_fits:
                    baseline_y -= line_height
                    x_pos = self.MARGIN_LEFT

                for letter in word:
                    if letter.lower() in self.keymap:
                        self.draw_letter(
                            self.ax,
                            self.keymap[letter.lower()],
                            (x_pos, baseline_y),
                            self.size,
                            show_letters=show_letters,
                            letter_position=letter_position,
                            dotted_guidelines=dotted_guidelines,
                            letter_char=letter
                        )
                        x_pos += letter_box_width
                        
                    else:
                        print(f"Letra no encontrada en keymap: '{letter}'")

                if not trim_words: 
                    x_pos += letter_box_width

            baseline_y -= line_height
            x_pos = self.MARGIN_LEFT

    def generate_text_encoded(self, input_content, letter_spacing=0.4, line_spacing=0.6):
        """
        Esta función genera el texto codificado (sin letras visibles).
        """
        self.fig, self.ax = plt.subplots(figsize=(12, 8))

        self.draw_text(
            input_content,
            letter_spacing=letter_spacing,
            line_spacing=line_spacing,
            show_letters=False,
            letter_position='none',
            dotted_guidelines=True
        )

        self.ax.set_xlim(0, self.SCREEN_WIDTH)
        self.ax.set_ylim(0, self.SCREEN_HEIGHT)
        self.ax.axis('off')

    def generate_text_solution(self, input_content, letter_spacing=0.4, line_spacing=0.6):
        """
        Esta función genera el texto cifrado con las letras debajo.
        """
        self.fig, self.ax = plt.subplots(figsize=(12, 8))

        self.draw_text(
            input_content,
            letter_spacing=letter_spacing,
            line_spacing=line_spacing,
            show_letters=True,
            letter_position='below',
            dotted_guidelines=True
        )

        self.ax.set_xlim(0, self.SCREEN_WIDTH)
        self.ax.set_ylim(0, self.SCREEN_HEIGHT)
        self.ax.axis('off')

    def generate_abc(self, letter_spacing=0.4, line_spacing=0.6):
        """
        Esta función genera el abecedario completo con letras debajo.
        """
        abc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        abc_line = [abc]

        self.fig, self.ax = plt.subplots(figsize=(12, 8))

        self.draw_text(
            abc_line,
            letter_spacing=letter_spacing,
            line_spacing=line_spacing,
            show_letters=True,
            letter_position='below',
            dotted_guidelines=True
        )

        self.ax.set_xlim(0, self.SCREEN_WIDTH)
        self.ax.set_ylim(0, self.SCREEN_HEIGHT)
        self.ax.axis('off')

    def save_output(self, output_filename):
        """
        Guarda la figura actual en el archivo de salida.
        """
        if self.fig:
            self.fig.savefig(output_filename, bbox_inches='tight', dpi=300)
            print(f"Archivo generado exitosamente: {output_filename}")
        else:
            print("Error: no hay figura para guardar.")
