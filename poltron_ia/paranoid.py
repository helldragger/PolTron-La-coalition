import random
"""
        author: Vincent DE MENEZES
"""
def printMapScope(scope, lenRow, lenCol):
    grid = [0] * lenRow
    sting = []
    for i in range(len(grid)):
        grid[i] = [0] * lenCol
    for (row,col) in scope:
        grid[row][col] = scope.get((row,col))
    for i in range(len(grid)):
       print(grid[i]) 

def initDictionary(dictionaryPlayers): 
    dictionaryMap = {"players" : {"attacker" : [], "defender" : []}, "scope" : {}}
    for team, players in dictionaryPlayers:
        for p in players:
            dictionaryMap["scope"][p] = 0
    return dictionaryMap

def hasNextPlayer(board, team, indexPlayer):
    if indexPlayer < len(board["players"][team]) - 1:
        return True
    return False

def isMoveVoid(self, team, indexP, sens):
    move = ["D", "Q", "Z", "S"]
    while sens == '':
        sens = random.choice(move)
        if self.isDying(self.nextMove(self.board["players"][team][indexP], sens)):
            move.remove(sens)
            sens = ''
            if len(move) == 0:
                sens = "D"
    return sens

def reverseTeam(team):
    if team == "attacker":
        return "defender"
    return "attacker"

def rangeControl(self, initialPosition, allies, indicator):
    enemies = reverseTeam(allies)
    stack = []
    visited = []
    stack.append(initialPosition)
    while stack:
        coord = stack[-1]
        stack.pop()
        visited.append(coord)
        for move in [[1,0], [-1, 0], [0,1], [0,-1]]:
            scope = indicator["scope"].get(coord) + 1
            row, col = coord[0] + move[0], coord[1] + move[1]
            if not self.isDying((row,col)) and not (row,col) in visited:
                if not (row,col) in indicator["scope"]:
                    indicator["scope"][(row,col)] = scope
                    indicator["players"][allies].append((row,col))
                    stack.insert(0, (row,col))
                elif indicator["scope"].get((row,col)) >= scope:
                    if indicator["scope"].get((row,col)) > scope:
                        indicator["scope"][(row,col)] = scope
                        stack.insert(0, (row,col))
                        if not (row,col) in indicator["players"][allies]:
                            indicator["players"][allies].append((row,col))
                    if (row,col) in indicator["players"][enemies]:
                        indicator["players"][enemies].remove((row,col))

def heuristic(self, targetTeam):
    mapIndicator = initDictionary(self.board["players"].items())
    for team, players in self.board["players"].items():
        for p in players:
            rangeControl(self, p, team, mapIndicator)
    lenAllies = len(mapIndicator["players"][targetTeam])
    lenEnnemies = len(mapIndicator["players"][reverseTeam(targetTeam)])
    size = lenAllies + lenEnnemies + 1
    h = lenAllies / size * 100
    return h

def algorithmParanoid(game, depth, team, p, indexP):
    void, move = alphabeta(game, depth, team, indexP, team, -1000, 1000)
    return move

def alphabeta(game, depth, team, indexP, original, a, b):
    if depth == 0 or game.endGame():
       return heuristic(game, original), ''
    best = -1000
    sens = ''
    nextPlayer = hasNextPlayer(game.board, team, indexP)
    for move in ["D", "Q", "Z", "S"]:
        indexDeath = 1
        cloneBoard = game.copy()
        nextMove = cloneBoard.nextMove(game.board["players"][team][indexP], move)
        cloneBoard.board["wall"].append(game.board["players"][team][indexP])
        if cloneBoard.isDying(nextMove):
            cloneBoard.board["players"][team].remove(game.board["players"][team][indexP])
            indexDeath = 0
        else:
            cloneBoard.board["players"][team][indexP] = nextMove 
        if nextPlayer:
            indexPlayer = indexP + (1 * indexDeath)
            v, void = alphabeta(cloneBoard, depth - 1, team, indexPlayer, original, a, b)
        elif indexDeath == 0:
            continue
        else:
            v, void = alphabeta(cloneBoard, depth - 1, reverseTeam(team), 0, original, -1 * b, -1 * a)
            v = -v 
        if v > best:
            best = v
            sens = move
            if best > a:
                a = best
                if a >= b:
                    return best, sens
    sens = isMoveVoid(game, team, indexP, sens)
    return best, sens

