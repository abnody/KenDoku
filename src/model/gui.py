# gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from puzzle import KenKenPuzzle
from cell import KenKenCell

class KenKenGUI:
     def __init__(self):
        self.root = tk.Tk()
        self.root.title("KenKen Puzzle")
        self.root.configure(bg='white')

        top = ttk.Frame(self.root)
        top.pack(side=tk.TOP, fill=tk.X, padx=10, pady=8)

        title = ttk.Label(top, text="KenKen Puzzle", font=('Arial', 20, 'bold'))
        title.pack(side=tk.LEFT, padx=(2,12))

        size_frame = ttk.Frame(top)
        size_frame.pack(side=tk.LEFT, padx=6)
        ttk.Label(size_frame, text="Grid size:").pack(side=tk.LEFT)
        self.size_var = tk.StringVar(value="4")
        self.size_combobox = ttk.Combobox(size_frame, textvariable=self.size_var, state="readonly",
                                          values=["4","5","6","7","8"], width=3)
        self.size_combobox.pack(side=tk.LEFT, padx=(4,10))

        btn_start = ttk.Button(size_frame, text="Start Game", command=self.start_game)
        btn_start.pack(side=tk.LEFT)

        controls = ttk.Frame(top)
        controls.pack(side=tk.RIGHT, padx=6)
        self.btn_new = ttk.Button(controls, text="New Puzzle", command=self.new_puzzle, state=tk.DISABLED)
        self.btn_new.pack(side=tk.LEFT, padx=4)
        self.btn_check = ttk.Button(controls, text="Check", command=self.check_solution, state=tk.DISABLED)
        self.btn_check.pack(side=tk.LEFT, padx=4)
        self.btn_show = ttk.Button(controls, text="Show Solution", command=self.show_solution_popup, state=tk.DISABLED)
        self.btn_show.pack(side=tk.LEFT, padx=4)

    
        self.container = ttk.Frame(self.root)
        self.container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    
        self.grid_frame = None
        self.puzzle = None
        self.cells = []
        self.cell_size = 70

     def start_game(self):
        try:
            size = int(self.size_var.get())
        except:
            messagebox.showerror("Error", "Choose a valid size.")
            return
        self.init_puzzle(size)
        self.btn_new.config(state=tk.NORMAL)
        self.btn_check.config(state=tk.NORMAL)
        self.btn_show.config(state=tk.NORMAL)

     def init_puzzle(self, size):
        if self.grid_frame:
            self.grid_frame.destroy()
        self.cells = []
        self.puzzle = KenKenPuzzle(size)
        self.puzzle.generate_puzzle()

        self.grid_frame = ttk.Frame(self.container)
        self.grid_frame.pack()

    
        base = max(40, int(420 / size))
        self.cell_size = base

        for i in range(size):
            row = []
            for j in range(size):
                cell = KenKenCell(self.grid_frame, size=self.cell_size, relief=tk.FLAT)
                cell.grid(row=i, column=j, padx=0, pady=0)
                row.append(cell)
            self.cells.append(row)

        self.setup_puzzle_visuals()

     def setup_puzzle_visuals(self):
        size = self.puzzle.size
        for r in range(size):
            for c in range(size):
                self.cells[r][c].set_operation("")
                self.cells[r][c].set_value(0)
                self.cells[r][c].highlight(None)

        for cells, operation, target in self.puzzle.cages:
           
            first = min(cells, key=lambda x: (x[0], x[1]))
            op_text = f"{target}{operation}"
            self.cells[first[0]][first[1]].set_operation(op_text)

            for i, j in cells:
                borders = {"top":1,"right":1,"bottom":1,"left":1}
                for di, dj, side in [(-1,0,"top"), (1,0,"bottom"), (0,-1,"left"), (0,1,"right")]:
                    ni, nj = i+di, j+dj
                    if 0 <= ni < size and 0 <= nj < size and (ni, nj) in cells:
                        borders[side] = 1
                    else:
                        borders[side] = 4
                self.cells[i][j].set_borders(borders)

     def new_puzzle(self):
        if not self.puzzle:
            return
        size = self.puzzle.size
        self.puzzle = KenKenPuzzle(size)
        self.puzzle.generate_puzzle()
        self.setup_puzzle_visuals()

     def check_solution(self):
        if not self.puzzle:
            return
        size = self.puzzle.size
        for r in range(size):
            for c in range(size):
                self.cells[r][c].highlight(None)

        grid_vals = [[self.cells[r][c].get_value() for c in range(size)] for r in range(size)]

       
        incomplete = any(grid_vals[r][c] == 0 for r in range(size) for c in range(size))
        if incomplete:
            if not messagebox.askyesno("Incomplete", "The grid is not completely filled. Check only filled cells anyway?"):
                return

        wrong_cells = set()

        for r in range(size):
            seen = {}
            for c in range(size):
                v = grid_vals[r][c]
                if v == 0: continue
                if v < 1 or v > size:
                    wrong_cells.add((r,c))
                if v in seen:
                    wrong_cells.add((r,c))
                    wrong_cells.add((r,seen[v]))
                else:
                    seen[v] = c
        for c in range(size):
            seen = {}
            for r in range(size):
                v = grid_vals[r][c]
                if v == 0: continue
                if v in seen:
                    wrong_cells.add((r,c))
                    wrong_cells.add((seen[v],c))
                else:
                    seen[v] = r

   
        for cells, operation, target in self.puzzle.cages:
            vals = [grid_vals[r][c] for r,c in cells]
            if any(v == 0 for v in vals):
                continue
            
            is_correct = False
            if operation == "+":
                is_correct = sum(vals) == target
            elif operation == "-":
                is_correct = len(vals) == 2 and abs(vals[0] - vals[1]) == target
            elif operation == "*":
                prod = 1
                for v in vals: prod *= v
                is_correct = prod == target
            elif operation == "/":
                if len(vals) == 2:
                    a,b = vals
                    is_correct = (b != 0 and a % b == 0 and a // b == target) or \
                                 (a != 0 and b % a == 0 and b // a == target)
            elif operation == "":
                is_correct = len(vals) == 1 and vals[0] == target
                
            if not is_correct:
                for cell in cells: wrong_cells.add(cell)

        for r in range(size):
            for c in range(size):
                v = grid_vals[r][c]
                if (r,c) in wrong_cells:
                    
                    self.cells[r][c].highlight('#ffcccc') 
                else:
                    if v != 0:
                     
                        self.cells[r][c].highlight('#ccffcc')  

        if not wrong_cells and not incomplete:
            messagebox.showinfo("Great!", "The solution is completely correct! 🎉")
        elif not wrong_cells and incomplete:
            messagebox.showinfo("Great!", "All checked cells look correct! 🎉")
        else:
            messagebox.showinfo("Check finished", f"Found {len(wrong_cells)} cells that may be wrong (highlighted).")

     def show_solution_popup(self):
        if not self.puzzle:
            return
        popup = tk.Toplevel(self.root)
        popup.title("Solution")
        popup.configure(bg='white')
        size = self.puzzle.size

        lbl = ttk.Label(popup, text=f"Solution ({size} x {size})", font=('Arial', 14, 'bold'))
        lbl.pack(padx=8, pady=8)

        grid_frame = ttk.Frame(popup)
        grid_frame.pack(padx=8, pady=8)

     
        for r in range(size):
            for c in range(size):
                val = self.puzzle.solution[r][c]
              
                lbl_cell = tk.Label(grid_frame, text=str(val), font=('Arial', 12, 'bold'),
                                     width=3, height=1, relief=tk.RIDGE, bg='white')
                lbl_cell.grid(row=r, column=c, padx=1, pady=1)

        btn_close = ttk.Button(popup, text="Close", command=popup.destroy)
        btn_close.pack(pady=6)

     def run(self):
        self.root.mainloop()
