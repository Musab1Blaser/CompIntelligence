import random
pop_size = 100
children_per_gen = 2*50
n = 32
num_generations = 10000
mutation_rate = 0.5

# 1 queen per column - allele represents row number, so only diagonal collisions to account for

def eval_fitness(lst):
    collisions = 0
    diag_freq = [0]*(2*n - 1)
    off_diag_freq = [0]*(2*n - 1)
    for qcol, qrow in enumerate(lst):
        diag = qcol + (n - qrow) - 1 # determine main diagonal - bottom left is 0
        off_diag = (n - qcol) + (n - qrow) - 2 # determine off diagonal - bottom right is 0
        # print(diag, off_diag)
        diag_freq[diag] += 1
        off_diag_freq[off_diag] += 1
    
    for i in range(2*n - 1):
        collisions += diag_freq[i]*(diag_freq[i] - 1) + off_diag_freq[i]*(off_diag_freq[i] - 1) # queens on same diag collide
    
    fitness = n**2 - collisions # max collisions is every queen colliding with each other
    return fitness

def eval_fitness_all(population):
    fitness = []
    for opt in population:
        fitness.append(eval_fitness(opt))
    return fitness

def selection(fitness_prop, num):
    sigma = random.random()*(1/num)
    selected = []
    i = 0
    cur = fitness_prop[0]
    while i < pop_size and sigma < 1:
        if sigma < cur:
            selected.append(i)
            sigma += 1/num
        else:
            i += 1
            cur += fitness_prop[i]
    return selected

def mutate_child(child):
    if random.random() > mutation_rate:
        return
    idx1 = random.randint(0, n-1)
    idx2 = random.randint(0, n-1)
    child[idx1], child[idx2] = child[idx2], child[idx1]

def generate_child_pair(parent1, parent2):
    crossover_point1 = random.randint(0, n-1)
    crossover_point2 = (crossover_point1 + random.randint(2, n-2)) % n # at least 2 genes from each parent
    child1 = [-1]*n
    child2 = [-1]*n
    idx = crossover_point1
    while idx != crossover_point2:
        child1[idx] = parent1[idx]
        child2[idx] = parent2[idx]
        idx = (idx + 1) % n
    
    idx1 = idx
    idx2 = idx
    while idx != crossover_point1:
        while parent2[idx1] in child1:
            idx1 = (idx1 + 1) % n
        while parent1[idx2] in child2:
            idx2 = (idx2 + 1) % n
            
        child1[idx] = parent2[idx1]
        child2[idx] = parent1[idx2]
        idx = (idx + 1) % n
        
    mutate_child(child1)
    mutate_child(child2)
    
    return [child1, child2]

def generate_children(population, parents):
    children = []
    for i in range(children_per_gen//2):
        idx1, idx2 = random.sample(parents, 2)
        children.extend(generate_child_pair(population[idx1], population[idx2]))
    return children

# print(eval_fitness([7, 2, 5, 1, 3, 0, 6, 4]))

# initialise
population = []
for i in range(pop_size):
    lst = list(range(n))
    random.shuffle(lst)
    population.append(lst)
    
generation = 0
best_fitness = 0
best_opt = [1]*n


while generation < num_generations and best_fitness != n**2:
    fitness = eval_fitness_all(population)
    total = sum(fitness)
    fitness_prop = [i/total for i in fitness]
    
    parents = selection(fitness_prop, children_per_gen)
    if len(parents) % 2:
        parents.pop()
    # print(parents)
    population.extend(generate_children(population, parents))
    
    fitness = eval_fitness_all(population)
    total = sum(fitness)
    fitness_prop = [i/total for i in fitness]
    
    best_fitness = max(fitness)
    best_opt = population[fitness.index(best_fitness)]
    
    survivors = selection(fitness_prop, pop_size)
    population = [population[i] for i in survivors]
    while len(population) < pop_size:
        population.append(best_opt)
    
    # print(best_opt)
    generation += 1
    # print(len(population))
    print(n**2 - best_fitness)
print(best_opt)