import random
import functools
from collections import defaultdict
from evaluate import evaluate


class genetic_algoritgm:
    
    def __init__(self, populationSize, generation, mutationRate, crossoverRate):
        self.populationSize = populationSize
        self.generation = generation
        self.mutationRate = mutationRate
        self.crossoverRate = crossoverRate
        self.population = []
        self.names_of_pieces = ["spy", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "bomb", "flag"]
        self.starting_quantities = {"bomb"  : 6,
                                "one"   : 1,
                                "two"   : 1,
                                "three" : 2,
                                "four"  : 3,
                                "five"  : 4,
                                "six"   : 4,
                                "seven" : 4,
                                "eight" : 5,
                                "nine"  : 8,
                                "spy"   : 1,
                                "flag"  : 1}


    def random_board_layout(self):
        board = []
        board_columns = 10
        row = []
        n = 0
        pieces_used = defaultdict(lambda: 0)
        while n < 40:
            piece = random.choice(self.names_of_pieces)
            if pieces_used[piece] < self.starting_quantities[piece]:
                row.append(f"{piece}")
                pieces_used[piece] += 1
                n += 1
                if len(row) == board_columns:
                    board.append(row)
                    row = []
        return board
    
    def createPopulation(self):
        for i in range(self.populationSize):
            randomBoard = self.random_board_layout()
            self.population.append(randomBoard)
        self.population = sorted(self.population, key= functools.cmp_to_key(compare))


    def evaluate(self, board):
        """evalutes the board and returns a fitness score)"""
        return evaluate(board)

    def calculate_fitness_probabilities(self):
        fitnessScore = []
        totalFitness = ((self.populationSize + 1) * self.populationSize) / 2
        probabilities = []
        for idx,board in enumerate(self.population):
            probabilities.append((idx+1)/totalFitness)
        return probabilities


    def rouletteSelection(self, probabilities):
        randomNumbers = []
        for i in range(len(self.population)):
            randomNumbers.append(random.random())
       
        cumulativeProbabilities = [sum(probabilities[:x+1]) for x in range(len(probabilities))]
        newPopulation = []
        for r in randomNumbers:
            for x in range(len(cumulativeProbabilities)):
                if(x == 0):
                    if r > 0 and r <= cumulativeProbabilities[x]:
                        newPopulation.append(self.population[x])
                else:
                    if r > cumulativeProbabilities[x-1] and r <cumulativeProbabilities[x]:
                        newPopulation.append(self.population[x])
        return newPopulation

    def create_offspring(self, parent1, parent2):
        """This method takes two parents and creates an offspring using crossover and mutation"""
        child = [[" "] * 10 for _ in range(4)]
        current_board = current_board = { k: 0 for k in self.starting_quantities.keys() }
        crossover_point = random.randint(0, 9)
        parent1, parent2 = random_swap_list(parent1, parent2)
        for i in range(4):
            for j in range(crossover_point):
                child[i][j] = parent1[i][j]
                current_board[parent1[i][j]] += 1

        for i in range(4):
            for j in range(crossover_point+1, 9):
                if (current_board[parent2[i][j]] < self.starting_quantities[parent2[i][j]]):
                    child[i][j] = parent2[i][j]
                    current_board[parent2[i][j]] += 1

        remaining_pieces = []
        for key in self.starting_quantities:
            if (current_board[key] < self.starting_quantities[key]):
                for _ in range(self.starting_quantities[key] - current_board[key]):
                    remaining_pieces.append(key)
        
        random.shuffle(remaining_pieces)

        k = 0
        for i in range(4):
            for j in range(10):
                if child[i][j] == " ":
                    child[i][j] = remaining_pieces[k]
                    k+=1

        return child

    def crossover(self):
        crossoverParents = []
        for i in range(len(self.population)):
            r = random.random()
            if r < self.crossoverRate:
                crossoverParents.append(self.population[i])
        
        for x in range(len(crossoverParents)):
            parent1 = crossoverParents[x]
            if x == (len(crossoverParents) - 1):
                parent2 = crossoverParents[0]
            else:
                parent2 = crossoverParents[x+1]
        
            child = self.create_offspring(parent1, parent2)
            self.population[x] = child

    
    def execute(self):
        #self.createPopulation()
        for _ in range(self.generation):
            probabilities = self.calculate_fitness_probabilities()
            self.population = self.rouletteSelection(probabilities)
            self.population = sorted(self.population, key= functools.cmp_to_key(compare))
            self.crossover()

    def get_best_board(self):
        maximum = -1
        bestboard = []
        for board in self.population:
            score = self.evaluate(board)
            if score > maximum:
                maximum = score
                bestboard = board
        
        return bestboard, maximum

            



def is_board_valid(board):
    starting_quantities = {"bomb"  : 6,
                           "one"   : 1,
                           "two"   : 1,
                           "three" : 2,
                           "four"  : 3,
                           "five"  : 4,
                           "six"   : 4,
                           "seven" : 4,
                           "eight" : 5,
                           "nine"  : 8,
                           "spy"   : 1,
                           "flag"  : 1}

    current_board = { k: 0 for k in starting_quantities.keys() }
    for row in board:
        for piece in row:
            current_board[piece] += 1
    
    if (current_board == starting_quantities):
        return True
    
    return False
        

            
def random_swap_list(list1 , list2):
    r = random.random()
    if r <= 0.5:
        return list1, list2
    return list2, list1


def compare(board1, board2):
    if (evaluate(board1) < evaluate(board2)):
        return -1
    elif (evaluate(board1) > evaluate(board2)):
        return 1
    else:
        return 0 



def main():

    ga = genetic_algoritgm(100, 10000, 0.4, 0.6)
    ga.createPopulation()
    board, score = ga.get_best_board()
    print(score)
    for rows in board:
        print(rows)
    ga.execute()
    board, score = ga.get_best_board()
    print("After ", score)
    for rows in board:
        print(rows)

    """l = []
    for board in ga.population:
        l.append(ga.evaluate(board))
    ga.population = ga.rouletteSelection(ga.calculate_fitness_probabilities())
    print(l)
    j = []
    for board in ga.population:
        j.append(ga.evaluate(board))
    print(j)"""
        



if __name__ == "__main__":
    main()

