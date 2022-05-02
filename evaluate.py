def evaluate(board):
    return defense_around_flag(board)

def get_flag_location(board):
    for i in range(4):
        for j in range(10):
            if (board[i][j] == "flag"):
                return i,j

    return -1, -1

def defense_around_flag(board):
    score = 0
    flagx, flagy = get_flag_location(board)
    if flagx == 0:
        score += 100
    score += abs(5- flagy) * 10
    bombs = get_bombs_locations(board)
    for bomb in bombs:
        x, y = bomb[0], bomb[1]
        if (abs(flagx - x) <= 1 and abs(flagy - y) <= 1):
            score += 20
    
    marshalx , marshaly = get_marshal_loaction(board)
    dis = (abs(flagx - marshalx) + abs(flagy - marshaly))
    score+= abs(14 - dis) * 10
    return score
    

def get_bombs_locations(board):
    x = []
    for i in range(4):
        for j in range(10):
            if (board[i][j] == "bomb"):
                x.append((i,j))
    return x


    
def get_marshal_loaction(board):
    for i in range(4):
        for j in range(10):
            if (board[i][j] == "one"):
                return i, j