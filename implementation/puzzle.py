import random

class KenKenPuzzle:
    def __init__(self, size: int):
        self.size = size
        self.grid = [[0 for _ in range(size)] for _ in range(size)]
        self.cages = []
        self.solution = None

    def generate_puzzle(self):
        self.solution = self._generate_solution()
        self._generate_cages()

    def _generate_solution(self):
        solution = [[0 for _ in range(self.size)] for _ in range(self.size)]

        def is_valid(num, row, col):
            for x in range(self.size):
                if solution[row][x] == num or solution[x][col] == num:
                    return False
            return True

        def solve():
            for r in range(self.size):
                for c in range(self.size):
                    if solution[r][c] == 0:
                        nums = list(range(1, self.size + 1))
                        random.shuffle(nums)
                        for num in nums:
                            if is_valid(num, r, c):
                                solution[r][c] = num
                                if solve():
                                    return True
                                solution[r][c] = 0
                        return False
            return True

        solve()
        return solution

    def _generate_cages(self):
        self.cages = []
        used_cells = set()

        while len(used_cells) < self.size * self.size:
            available_cells = [(i, j) for i in range(self.size) for j in range(self.size)
                               if (i, j) not in used_cells]
            start_cell = random.choice(available_cells)
            cage_cells = [start_cell]
            used_cells.add(start_cell)

            cage_size = random.randint(1, min(4, self.size))

            while len(cage_cells) < cage_size:
                potential = []
                for current in cage_cells:
                    adj = [(current[0]+di, current[1]+dj) for di, dj in [(0,1),(1,0),(0,-1),(-1,0)]
                           if 0 <= current[0]+di < self.size and 0 <= current[1]+dj < self.size and
                           (current[0]+di, current[1]+dj) not in used_cells]
                    potential.extend(adj)
                if not potential:
                    break
                next_cell = random.choice(potential)
                cage_cells.append(next_cell)
                used_cells.add(next_cell)

            values = [self.solution[i][j] for i, j in cage_cells]

            if len(cage_cells) == 1:
                operation = ""
                target = values[0]
            else:
                r = random.random()
                if r < 0.4:
                    operation = "+"
                    target = sum(values)
                elif r < 0.7:
                    operation = "*"
                    prod = 1
                    for v in values: prod *= v
                    target = prod
                else:
                    if len(cage_cells) == 2:
                        a, b = values
                        if random.random() < 0.5:
                            operation = "-"
                            target = abs(a-b)
                        else:
                            if a != 0 and b != 0 and (a % b == 0 or b % a == 0):
                                operation = "/"
                                target = max(a//b, b//a)
                            else:
                                operation = "-"
                                target = abs(a-b)
                    else:
                        operation = "+"
                        target = sum(values)

            self.cages.append((cage_cells, operation, target))
