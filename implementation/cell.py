# cell.py
import tkinter as tk
from tkinter import ttk

class KenKenCell(tk.Frame):
    def __init__(self, master, size=70, **kwargs):
        super().__init__(master, width=size, height=size, **kwargs)
        self.size = size
        self.pack_propagate(False)

        self.canvas = tk.Canvas(self, width=size, height=size, highlightthickness=0, bg='#F8FBF8')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.value = tk.StringVar()
        vcmd = (self.register(self._validate_digit), '%P')

        self.entry = ttk.Entry(
            self.canvas, width=2, justify="center",
            textvariable=self.value, font=('Arial', 20, 'bold'),
            validate='key', validatecommand=vcmd
        )

        self.canvas.create_window(size/2, size/2, window=self.entry)

        self.borders = {"top":1, "right":1, "bottom":1, "left":1}
        self.operation_text = ""
        self.bg_rect = self.canvas.create_rectangle(0,0,size,size, fill='#F8FBF8', outline='#F8FBF8')

    def _validate_digit(self, P):
        if P == "":
            return True
        return P.isdigit() and len(P) <= 2

    def set_borders(self, borders):
        self.borders = borders
        self.redraw()

    def set_operation(self, text):
        self.operation_text = text
        self.redraw()

    def set_value(self, val):
        self.value.set(str(val) if val != 0 else "")

    def get_value(self):
        s = self.value.get().strip()
        return int(s) if s.isdigit() else 0

    def highlight(self, color=None):
        if color:
            self.canvas.itemconfig(self.bg_rect, fill=color)
        else:
            self.canvas.itemconfig(self.bg_rect, fill='#F8FBF8')

    def redraw(self):
        self.canvas.delete("borders")
        size = self.size

        self.canvas.coords(self.bg_rect, 0, 0, size, size)

        for side, width in self.borders.items():
            if width > 0:
                fill_color = '#371D10'
                if side == "top":
                    self.canvas.create_line(0,0,size,0,width=width,fill=fill_color,tags="borders")
                elif side == "right":
                    self.canvas.create_line(size,0,size,size,width=width,fill=fill_color,tags="borders")
                elif side == "bottom":
                    self.canvas.create_line(0,size,size,size,width=width,fill=fill_color,tags="borders")
                elif side == "left":
                    self.canvas.create_line(0,0,0,size,width=width,fill=fill_color,tags="borders")

        if self.operation_text:
            pad = 4
            self.canvas.create_rectangle(pad, pad, size/2 + pad, size/4 + pad/2,
                                         fill='#F8FBF8', outline='#F8FBF8', tags="op_bg")
            self.canvas.create_text(
                pad + 2, pad + 2,
                text=self.operation_text,
                anchor=tk.NW,
                font=('Arial',9,'bold'),
                fill='#6F4685',
                tags="borders"
            )

        self.canvas.create_window(size/2, size/2, window=self.entry)
