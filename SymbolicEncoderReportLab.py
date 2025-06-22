# symbolic_encoder.py

import json
import unicodedata
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class SymbolicEncoder:
    LINES_MAP = {
        "bottom_left":    [10, 30, 20, 15],
        "bottom_right":   [30, 30, 20, 15],
        "center":         [10, 30, 30, 30],
        "top_left":       [10, 30, 20, 45],
        "top_right":      [30, 30, 20, 45],
    }

    def __init__(self, keymap_file, size, screen_width=612, screen_height=792, margin_left=40, margin_right=40, initial_baseline=700):
        self.page_width, self.page_height = letter
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

    def draw_letter(self, c, letter_config, position, size, show_letters=False, letter_position='below', letter_char=None):
        x_offset, baseline_y = position
        scale = size / 50

        for line_key in letter_config:
            if line_key and line_key in self.LINES_MAP:
                x1, y1, x2, y2 = self.LINES_MAP[line_key]

                x1 = x_offset + x1 * scale
                x2 = x_offset + x2 * scale
                y1 = baseline_y - (y1 * scale)
                y2 = baseline_y - (y2 * scale)

                c.setLineWidth(2)
                c.line(x1, y1, x2, y2)
            else:
                print(f"Advertencia: línea '{line_key}' no existe en LINES_MAP")

        if show_letters and letter_char:
            if letter_position == 'below':
                c.setFont("Helvetica", size * 0.2)
                c.drawCentredString(
                    x_offset + (size * 0.4),
                    baseline_y - (size * 1.2),
                    letter_char.upper()
                )
            elif letter_position == 'inside':
                c.setFont("Helvetica", size * 0.4)
                c.drawCentredString(
                    x_offset + (size * 0.2),
                    baseline_y - (size * 0.5),
                    letter_char.upper()
                )

    def check_fit(self, word, x_pos, letter_box_spacing):
        word_width = len(word) * letter_box_spacing
        return (x_pos + word_width) <= (self.SCREEN_WIDTH - self.MARGIN_RIGHT)

    def draw_text(self, c, input_content, letter_spacing=0.4, line_spacing=0.6, show_letters=False, letter_position='below', trim_words=False):
        letter_box_width = self.size * letter_spacing
        line_height = self.size * line_spacing

        if show_letters and letter_position == 'below':
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
                            c,
                            self.keymap[letter.lower()],
                            (x_pos, baseline_y),
                            self.size,
                            show_letters=show_letters,
                            letter_position=letter_position,
                            letter_char=letter
                        )
                        x_pos += letter_box_width
                    else:
                        print(f"Letra no encontrada en keymap: '{letter}'")

                if not trim_words:
                    x_pos += letter_box_width

            baseline_y -= line_height
            x_pos = self.MARGIN_LEFT

    def generate_text_encoded(self, input_content, output_filename, letter_spacing=0.4, line_spacing=0.6):
        c = canvas.Canvas(output_filename, pagesize=letter)
        self.draw_text(
            c,
            input_content,
            letter_spacing=letter_spacing,
            line_spacing=line_spacing,
            show_letters=False,
            letter_position='none'
        )
        c.showPage()
        c.save()
        print(f"Archivo generado exitosamente: {output_filename}")

    def generate_text_solution(self, input_content, output_filename, letter_spacing=0.4, line_spacing=0.6):
        c = canvas.Canvas(output_filename, pagesize=letter)
        self.draw_text(
            c,
            input_content,
            letter_spacing=letter_spacing,
            line_spacing=line_spacing,
            show_letters=True,
            letter_position='below'
        )
        c.showPage()
        c.save()
        print(f"Archivo generado exitosamente: {output_filename}")

    def generate_abc(self, output_filename, letter_spacing=0.4, line_spacing=0.6):
        abc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        abc_line = [abc[i:i+5] for i in range(0, len(abc), 5)]

        c = canvas.Canvas(output_filename, pagesize=letter)
        self.draw_text(
            c,
            abc_line,
            letter_spacing=letter_spacing,
            line_spacing=line_spacing,
            show_letters=True,
            letter_position='below'
        )
        c.showPage()
        c.save()
        print(f"Archivo generado exitosamente: {output_filename}")
