import random
import pygame
import time
import matplotlib.pyplot as plt

pop_size = 100
children_per_gen = 2*int(0.2*pop_size)
n = 64
num_generations = 10000
mutation_rate = 0.6

# Flags to enable/disable visualizations
enable_pygame = True
enable_matplotlib = True

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

# Initialize Pygame
if enable_pygame:
    pygame.init()
    square_size = 20
    padding = 50
    screen_size = n * square_size + padding
    screen = pygame.display.set_mode((screen_size, screen_size))
    pygame.display.set_caption("N-Queens Visualization")
    font = pygame.font.SysFont(None, 24)

# Initialize Matplotlib
if enable_matplotlib:
    plt.ion()
    fig, ax = plt.subplots()
    line1, = ax.plot([], [], label='Best Fitness')
    line2, = ax.plot([], [], label='Mean Fitness')
    ax.legend()
    plt.xlabel('Generation')
    plt.ylabel('Collisions')
    xdata, ydata_best, ydata_mean = [], [], []

def draw_board(best_opt, best_fitness, generation):
    if not enable_pygame:
        return
    screen.fill((255, 255, 255))
    for row in range(n):
        for col in range(n):
            color = (0, 0, 0) if (row + col) % 2 == 0 else (255, 255, 255)
            pygame.draw.rect(screen, color, pygame.Rect(col * square_size + padding // 2, row * square_size + padding // 2, square_size, square_size))
    
    # Determine colliding queens
    diag_freq = [0]*(2*n - 1)
    off_diag_freq = [0]*(2*n - 1)
    for qcol, qrow in enumerate(best_opt):
        diag = qcol + (n - qrow) - 1
        off_diag = (n - qcol) + (n - qrow) - 2
        diag_freq[diag] += 1
        off_diag_freq[off_diag] += 1
    
    colliding_queens = set()
    for qcol, qrow in enumerate(best_opt):
        diag = qcol + (n - qrow) - 1
        off_diag = (n - qcol) + (n - qrow) - 2
        if diag_freq[diag] > 1 or off_diag_freq[off_diag] > 1:
            colliding_queens.add((qcol, qrow))
    
    for col, row in enumerate(best_opt):
        color = (255, 0, 0) if (col, row) in colliding_queens else (0, 255, 0)
        pygame.draw.circle(screen, color, (col * square_size + square_size // 2 + padding // 2, row * square_size + square_size // 2 + padding // 2), square_size // 2)
    
    score_text = font.render(f'Collisions: {n**2 - best_fitness}', True, (0, 0, 0))
    generation_text = font.render(f'Generation: {generation}', True, (0, 0, 0))
    screen.blit(score_text, (10, 10))
    screen.blit(generation_text, (screen_size-130, 10))
    pygame.display.flip()

def update_plot(generation, best_fitness, mean_fitness):
    if not enable_matplotlib:
        return
    xdata.append(generation)
    ydata_best.append(best_fitness)
    ydata_mean.append(mean_fitness)
    line1.set_data(xdata, ydata_best)
    line2.set_data(xdata, ydata_mean)
    ax.relim()
    ax.autoscale_view()
    # ax.set_xlim(0, max(10, generation))  # Ensure x-axis updates dynamically
    # ax.set_ylim(0, max(n))  # Ensure y-axis is fixed to n**2
    plt.draw()
    plt.pause(0.001)

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
    mean_fitness = sum(fitness) / len(fitness)
    
    survivors = selection(fitness_prop, pop_size)
    population = [population[i] for i in survivors]
    while len(population) < pop_size:
        population.append(best_opt)
    
    # print(best_opt)
    generation += 1
    # print(len(population))
    print(n**2 - best_fitness)
    draw_board(best_opt, best_fitness, generation)
    update_plot(generation, n**2 - best_fitness, n**2 - mean_fitness)
    if enable_pygame:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        time.sleep(0.1)  # Add a delay between each generation

# Keep the screen running
if enable_pygame:
    while True:
        draw_board(best_opt, best_fitness, generation)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
# print(best_opt)
# pygame.quit()