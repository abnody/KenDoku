import random
from copy import deepcopy
import matplotlib.pyplot as plt

size_configs = {
    4: {'pop_size': 300, 'generations': 500, 'elites_count': 15, 'retries': 5, 'rate':0.1},
    5: {'pop_size': 600, 'generations': 1000, 'elites_count': 20, 'retries': 20, 'rate':0.1},
    6: {'pop_size': 900, 'generations': 2000, 'elites_count': 30, 'retries': 90, 'rate':0.3}, 
    7: {'pop_size': 1400, 'generations': 3500, 'elites_count': 45, 'retries': 150, 'rate': 0.35},
    8: {'pop_size': 2000, 'generations': 6000, 'elites_count': 60, 'retries': 250, 'rate': 0.4},
    9: {'pop_size': 2800, 'generations': 9000, 'elites_count': 80, 'retries': 400, 'rate': 0.45},
}

class CulturalKenKenSolver:
    def __init__(self, puzzle, visualization_callback=None):
        self.puzzle = puzzle
        self.size = puzzle.size
        self.visualization_callback = visualization_callback

        self.pop_size = size_configs[self.size]['pop_size']
        self.generations = size_configs[self.size]['generations']
        self.elites_count = size_configs[self.size]['elites_count']
        self.retries = size_configs[self.size]['retries']
        self.rate = size_configs[self.size]['rate']

        self.cages = getattr(self.puzzle, "cages", [])
        self.grid = [[0]*self.size for _ in range(self.size)]

        self.history_best = []
        self.history_avg = []

        self.belief_space = {
            "best_solution": None,
            "best_fitness": float("inf"),
            "cell_knowledge": {}
        }


    ############### generating individuals ###############
    def random_individual(self):
        grid = [[0]*self.size for _ in range(self.size)]

        for r in range(self.size):
            nums = list(range(1, self.size+1))
            random.shuffle(nums)
            for c in range(self.size):
                grid[r][c] = nums[c]

        return self._to_chromosome(grid)
    
    ############### helper functions ###############
    def _to_chromosome(self, grid):
        chrom = []
        for r in range(self.size):
            chrom.extend(grid[r])
        return chrom

    def _to_grid(self, ind):
        self.grid = [ind[r*self.size:(r+1)*self.size] for r in range(self.size)]


    ############### fitness function ###############
    def fitness(self, ind):
        f = 0
        size = self.size
        grid = [ind[r*size:(r+1)*size] for r in range(size)]

        for row in grid:
            f += size - len(set(row))
        for c in range(size):
            col = [grid[r][c] for r in range(size)]
            f += size - len(set(col))

        for cage in self.cages:
            if len(cage) == 3:
                cells, op, target = cage
            else:
                cells, target = cage
                op = None
            values = [grid[r][c] for r,c in cells]

            if len(cells)==1 or op in (None,''):
                if values[0]!=target: f+=1
            elif op=='+':
                if sum(values)!=target: f+=1
            elif op=='*':
                prod=1
                for v in values: prod*=v
                if prod!=target: f+=1
            elif op=='-':
                if len(values)==2 and abs(values[0]-values[1])!=target: f+=1
            elif op=='/':
                if len(values)==2 and values[0]!=0 and values[1]!=0:
                    if values[0]/values[1]!=target and values[1]/values[0]!=target: 
                        f+=1
                else: 
                    f+=1

        return f

    ############### update_belief_space function ###############
    def update_belief_space(self, best, best_fit):
        if best_fit < self.belief_space["best_fitness"]:
            self.belief_space["best_fitness"] = best_fit
            self.belief_space["best_solution"] = best

        if "position_freq" not in self.belief_space:
            self.belief_space["position_freq"] = {}

        for i, val in enumerate(best):
            if i not in self.belief_space["position_freq"]:
                self.belief_space["position_freq"][i] = {}
            self.belief_space["position_freq"][i][val] = \
                self.belief_space["position_freq"][i].get(val, 0) + 1

    ############### select_elites function ###############
    def select_elites(self):
        sorted_pop = sorted(self.population, key=self.fitness)
        pop = sorted_pop[:self.elites_count]
        pop.append(sorted_pop[random.randint(0,len(sorted_pop)-1)])
        pop.append(sorted_pop[random.randint(0,len(sorted_pop)-1)])
        return pop

    ############### crossover function ###############
    def crossover(self, p1,p2):
        child=[]
        for r in range(self.size):
            row1 = p1[r*self.size:(r+1)*self.size]
            row2 = p2[r*self.size:(r+1)*self.size]
            child.extend(random.choice([row1,row2]))
        return child

    ############### mutate function ###############
    def mutate(self, ind):
        size = self.size

        for r in range(size):
            if random.random() < self.rate:
                row_start = r * size
                row_end = row_start + size
                indices = list(range(row_start, row_end))

                i, j = random.sample(indices, 2)

                confidence_i = self.belief_space.get("position_freq", {}).get(i, {}).get(ind[i], 0)
                confidence_j = self.belief_space.get("position_freq", {}).get(j, {}).get(ind[j], 0)

                
                if confidence_i > confidence_j:
                    i, j = j, i

                ind[i], ind[j] = ind[j], ind[i]

        return ind

    
    ############### visualization function ###############
    def _visualize(self, ind):
        if not self.visualization_callback:
            return
        for r in range(self.size):
            for c in range(self.size):
                val = ind[r*self.size + c]
                self.visualization_callback(r, c, val)

    ############### main solver function ###############
    def solve(self):
        attempt=0
        solved=False
        while attempt<self.retries and not solved:
            print(f"\n=== Cultural Attempt {attempt+1}/{self.retries} ===")
            self.population = [self.random_individual() for _ in range(self.pop_size)]
            counter=0
            old_best=0
            new_best=0

            for gen in range(self.generations):
                elites = self.select_elites()
                best = elites[0]
                best_fit = self.fitness(best)
                new_best = best_fit
                self.update_belief_space(best,best_fit)

                avg_fit=sum(self.fitness(ind) for ind in self.population)/len(self.population)
                self.history_best.append(best_fit)
                self.history_avg.append(avg_fit)


                if best_fit==0:
                    print("Perfect Solution Found!")
                    self._to_grid(best)
                    try:
                        self.plot_history()
                    except Exception as e:
                        print("Plotting failed: ", e)
                    return True
                    

                if gen % 10 == 0:
                    print(f"Gen {gen} | Best Fitness: {best_fit}")
                    if new_best==old_best :
                        counter += 1 
                    else:
                        counter = 0
                    old_best = new_best

                new_pop = elites.copy()
                if counter==6:
                    counter=0
                    # if (True):
                    #     new_pop.extend([self.semi_organized_individual() for _ in range(int(self.pop_size*0.5))])
                    #     print(f"Injection with {int(self.pop_size*0.5)} semi-organized individuals due to stagnation.")
                    # else:
                    print("Cultural Stagnation → Restarting...")
                    break

                while len(new_pop)<self.pop_size:
                    p1,p2=random.sample(elites,2)
                    child=self.crossover(p1,p2)
                    child=self.mutate(child)
                    new_pop.append(child)

                self.population=new_pop
            attempt+=1

        print("\n Failed to reach perfect solution.")
        best_solution = self.belief_space["best_solution"]
        if best_solution:
            self._to_grid(best_solution)
        else:
            print("No valid solution found.")


        try:
            self.plot_history()
        except Exception as e:
            print("Plotting failed:", e)

        return best_solution

    ############### plotting function ###############
    def plot_history(self, filename="fitness_progress.png", show=True):
        if not self.history_best and not self.history_avg:
            print("No history to plot.")
            return

        plt.figure(figsize=(10, 6))
        if self.history_best:
            plt.plot(self.history_best, label="Best Fitness")
        if self.history_avg:
            plt.plot(self.history_avg, label="Average Fitness", alpha=0.7)
        plt.xlabel("Generation")
        plt.ylabel("Fitness")
        plt.title("Cultural Algorithm Progress")
        plt.legend()
        plt.grid(True)
        plt.savefig(filename)
        print(f"Plot saved as '{filename}'")
        if show:
            try:
                plt.show(block=False)
            except TypeError:
                plt.show()
        plt.close()
