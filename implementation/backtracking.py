import time

class KenKenSolver:
    def __init__(self, puzzle, visualization_callback=None):
        self.puzzle = puzzle
        self.size = puzzle.size
        self.cages = puzzle.cages
        self.grid = [[0]*self.size for _ in range(self.size)]
        self.visualization_callback = visualization_callback

    def is_valid(self, r, c, num):
        for i in range(self.size):
            if self.grid[r][i] == num or self.grid[i][c] == num:
                return False

        for cells, op, target in self.cages:
            if (r, c) in cells:
                values = []
                for x, y in cells:
                    if x == r and y == c:
                        values.append(num)
                    elif self.grid[x][y] != 0:
                        values.append(self.grid[x][y])
                if len(values) < len(cells):
                    return True

                if op == "+": return sum(values) == target
                if op == "*":
                    prod = 1
                    for v in values: prod *= v
                    return prod == target
                if op == "-":
                    a, b = values
                    return abs(a-b) == target
                if op == "/":
                    a, b = values
                    if b == 0 or a == 0: return False
                    return max(a/b, b/a) == target
                return values[0] == target
        return True

    def select_mrv_cell(self):
        min_vals = 10**9
        chosen = None
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == 0:
                    domain = [n for n in range(1, self.size+1) if self.is_valid(r,c,n)]
                    if len(domain) < min_vals:
                        min_vals = len(domain)
                        chosen = (r,c,domain)
        return chosen

    def forward_check(self, r, c, num):
        temp = self.grid[r][c]
        self.grid[r][c] = num
        for rr in range(self.size):
            for cc in range(self.size):
                if self.grid[rr][cc] == 0:
                    domain = [n for n in range(1, self.size+1) if self.is_valid(rr,cc,n)]
                    if len(domain) == 0:
                        self.grid[r][c] = temp
                        return False
        self.grid[r][c] = temp
        return True

    def solve(self):
        mrv = self.select_mrv_cell()
        if mrv is None:
            return True

        r, c, domain = mrv
        for num in domain:
            if self.visualization_callback:
                self.visualization_callback(r, c, num)

            if self.is_valid(r,c,num) and self.forward_check(r,c,num):
                self.grid[r][c] = num
                if self.solve():
                    return True
                self.grid[r][c] = 0
                if self.visualization_callback:
                    self.visualization_callback(r, c, 0)
        return False
