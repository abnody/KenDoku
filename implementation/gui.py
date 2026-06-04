# gui.py (معدلة)
import tkinter as tk
from tkinter import ttk, messagebox
from puzzle import KenKenPuzzle
from cell import KenKenCell
from backtracking import KenKenSolver
import time
from cultural_solver import CulturalKenKenSolver

class KenKenGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("KenKen Puzzle")
        self.root.configure(bg='#C5C6D0')

        top = ttk.Frame(self.root)
        top.pack(side=tk.TOP, fill=tk.X, padx=10, pady=8)
        title = ttk.Label(top, text="KenKen Puzzle", font=('Arial', 20, 'bold'))
        title.pack(side=tk.LEFT, padx=(2,12))
        size_frame = ttk.Frame(top)
        size_frame.pack(side=tk.LEFT,padx=6)

        ttk.Label(size_frame, text="Grid size:").pack(side=tk.LEFT)
        self.size_var = tk.StringVar(value="4")
        self.size_combobox = ttk.Combobox(size_frame, textvariable=self.size_var, state="readonly",
                                          values=["4","5","6","7","8"], width=3)
        self.size_combobox.pack(side=tk.LEFT, padx=(4,10))

        btn_start = ttk.Button(size_frame, text="Start Game", command=self.start_game)
        btn_start.pack(side=tk.LEFT)

        controls = ttk.Frame(top)
        controls.pack(side=tk.RIGHT, padx=6)

        ttk.Label(controls, text="Solve by:").pack(side=tk.LEFT)
        self.solve_var = tk.StringVar(value="Backtracking")
        self.solve_box = ttk.Combobox(controls,textvariable=self.solve_var, state="readonly",values=["Backtracking","Culutural"], width=12)
        self.solve_box.pack(side=tk.LEFT, padx=5)
        self.btn_solve = ttk.Button(controls, text="Solve", command=self.check_method)
        self.btn_solve.pack(side=tk.LEFT, padx=4)
        self.btn_solve.config(state=tk.DISABLED)
        self.btn_new = ttk.Button(controls, text="New Puzzle", command=self.new_puzzle, state=tk.DISABLED)
        self.btn_new.pack(side=tk.LEFT, padx=4)

        # حذف زر check
        # self.btn_check = ttk.Button(controls, text="Check", command=self.check_solution, state=tk.DISABLED)
        # self.btn_check.pack(side=tk.LEFT, padx=4)

        self.time_label = ttk.Label(controls, text="Time: 0.00s")
        self.time_label.pack(side=tk.LEFT, padx=6)

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
        self.btn_solve.config(state=tk.NORMAL)

    def init_puzzle(self, size):
        if self.grid_frame:
            self.grid_frame.destroy()
        self.cells = []

        self.puzzle = KenKenPuzzle(size)
        self.puzzle.generate_puzzle()

        self.grid_frame = ttk.Frame(self.container)
        self.grid_frame.pack()

        base = max(40, int(590 / size))
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

    def visualization_update(self, r, c, val):
        self.cells[r][c].set_value(val)
        self.root.update()
        time.sleep(0.02)

    def check_method(self):
     method = self.solve_box.get()
     self.solve(method)      

    def solve(self, method):

        if method == "Backtracking":
            solver = KenKenSolver(self.puzzle, visualization_callback=self.visualization_update)
        else:
            solver = CulturalKenKenSolver(self.puzzle, visualization_callback=self.visualization_update)

        start = time.time()
        ok = solver.solve()
        end = time.time()

        if ok:
            for r in range(self.puzzle.size):
                for c in range(self.puzzle.size):
                    self.cells[r][c].set_value(solver.grid[r][c])
            self.time_label.config(text=f"Time: {end-start:.2f}s")
            messagebox.showinfo("Solved!", f"Solved in {end-start:.2f} seconds")
        else:
            messagebox.showerror("Failed", "Couldn't find a solution.")

    def new_puzzle(self):
        size = self.puzzle.size
        self.puzzle = KenKenPuzzle(size)
        self.puzzle.generate_puzzle()
        self.setup_puzzle_visuals()
        self.time_label.config(text="Time: 0.00s")

    def run(self):
        self.root.mainloop()
