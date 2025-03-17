import random

# Asignación de valores de puntuación a cada pieza de ajedrez.
pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}

# Definición de constantes para representar situaciones de jaque mate, empate y profundidad de búsqueda.
CHECKMATE = 1000  # Puntuación para jaque mate
STALEMATE = 0     # Puntuación para empate
DEPTH = 3         # Profundidad de búsqueda para el algoritmo de decisión

def findRandomMove(validMoves):
    """
    Selecciona un movimiento aleatorio de la lista de movimientos válidos.
    :param validMoves: Lista de movimientos válidos.
    :return: Un movimiento aleatorio.
    """
    return validMoves[random.randint(0, len(validMoves) - 1)]

def findBestMove(gs, validMoves):
    """
    Encuentra el mejor movimiento posible.
    :param gs: Estado actual del juego (GameState).
    :param validMoves: Lista de movimientos válidos.
    :return: El mejor movimiento encontrado.
    """
    global nextMove
    nextMove = None  # Inicializa la variable global para almacenar el mejor movimiento
    random.shuffle(validMoves)  # Mezcla los movimientos para añadir aleatoriedad
    #findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)  # Llama al algoritmo MinMax sin poda
    findMoveMinMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, gs.whiteToMove) # Llama al algoritmo MinMax con poda  Alpha-Beta
    return nextMove  # Retorna el mejor movimiento encontrado

def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    """
    Implementación del algoritmo MinMax con recursión y sin poda alpha beta.
    :param gs: Estado actual del juego.
    :param validMoves: Lista de movimientos válidos.
    :param depth: Profundidad de búsqueda.
    :param whiteToMove: True si es el turno de las blancas, False si es el turno de las negras.
    :return: La puntuación del mejor movimiento.
    """
    global nextMove
    if depth == 0:  # Si se alcanza la profundidad máxima, evalúa el tablero
        return scoreMaterial(gs.board)
    
    if whiteToMove:  # Turno de las blancas (maximizar puntuación)
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)  # Realiza el movimiento
            nextMoves = gs.getValidMoves()  # Obtiene los movimientos válidos después del movimiento
            score = findMoveMinMax(gs, nextMoves, depth - 1, False)  # Llama recursivamente para el siguiente nivel
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:  # Si estamos en el nivel raíz, guarda el mejor movimiento
                    nextMove = move
            gs.undoMove()  # Deshace el movimiento para probar el siguiente
        return maxScore
    else:  # Turno de las negras (minimizar puntuación)
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore

def findMoveMinMaxAlphaBeta(gs, validMoves, depth, alpha, beta, isMaximizingPlayer):
    """
    Implementación del algoritmo MinMax con poda Alpha-Beta para optimizar la búsqueda.
    :param gs: Estado actual del juego.
    :param validMoves: Lista de movimientos válidos.
    :param depth: Profundidad de búsqueda.
    :param alpha: Valor alpha para la poda.
    :param beta: Valor beta para la poda.
    :param isMaximizingPlayer: True si es el turno de maximizar, False si es el turno de minimizar.
    :return: La puntuación del mejor movimiento.
    """
    global nextMove
    if depth == 0:  # Si se alcanza la profundidad máxima, evalúa el tablero
        return scoreBoard(gs)
    
    if isMaximizingPlayer:  # Turno de maximizar (blancas)
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMaxAlphaBeta(gs, nextMoves, depth - 1, alpha, beta, False)
            gs.undoMove()
            
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:  # Si estamos en el nivel raíz, guarda el mejor movimiento
                    nextMove = move
            
            alpha = max(alpha, score)  # Actualiza el valor de alpha
            if beta <= alpha:  # Poda Alpha-Beta
                break
        return maxScore
    else:  # Turno de minimizar (negras)
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMaxAlphaBeta(gs, nextMoves, depth - 1, alpha, beta, True)
            gs.undoMove()
            
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            
            beta = min(beta, score)  # Actualiza el valor de beta
            if beta <= alpha:  # Poda Alpha-Beta
                break
        return minScore

def scoreBoard(gs):
    """
    Evalúa la puntuación del tablero según la posición de las piezas.
    :param gs: Estado actual del juego.
    :return: Puntuación del tablero.
    """
    if gs.checkMate:  # Si hay jaque mate
        return -CHECKMATE if gs.whiteToMove else CHECKMATE
    elif gs.staleMate:  # Si hay empate
        return STALEMATE
    
    score = 0
    for row in gs.board:  # Recorre el tablero
        for square in row:
            if square[0] == 'w':  # Pieza blanca
                score += pieceScore[square[1]]
            elif square[0] == 'b':  # Pieza negra
                score -= pieceScore[square[1]]
    return score

def scoreMaterial(board):
    """
    Evalúa el material en el tablero basado en la puntuación de las piezas.
    :param board: Tablero de ajedrez.
    :return: Puntuación del material.
    """
    score = 0
    for row in board:  # Recorre el tablero
        for square in row:
            if square[0] == 'w':  # Pieza blanca
                score += pieceScore[square[1]]
            elif square[0] == 'b':  # Pieza negra
                score -= pieceScore[square[1]]
    return score

"""
# Implementaciones alternativas de algoritmos de búsqueda (comentadas)

def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMax(gs, nextMoves, depth-1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore

def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore
"""