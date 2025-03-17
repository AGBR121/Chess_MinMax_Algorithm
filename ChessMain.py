import pygame as p
import ChessEngine, SmartMoveFinder

# Dimensiones de la ventana del juego y del tablero
WIDTH = HEIGHT = 512  # Tamaño de la ventana (512x512 píxeles)
DIMENSION = 8  # Dimensiones del tablero (8x8 casillas)
SQ_SIZE = HEIGHT // DIMENSION  # Tamaño de cada casilla (64x64 píxeles)
MAX_FPS = 20  # Fotogramas por segundo para controlar la velocidad de la animación
IMAGES = {}  # Diccionario para almacenar las imágenes de las piezas

# Función para cargar las imágenes de las piezas
def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']  # Lista de piezas
    for piece in pieces:
        # Carga y escala cada imagen al tamaño de una casilla
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

# Función principal del juego
def main():
    p.init()  # Inicializa pygame
    screen = p.display.set_mode((WIDTH, HEIGHT))  # Crea la ventana del juego
    clock = p.time.Clock()  # Reloj para controlar los FPS
    screen.fill(p.Color("white"))  # Rellena la pantalla con color blanco
    gs = ChessEngine.GameState()  # Inicializa el estado del juego
    validMoves = gs.getValidMoves()  # Obtiene los movimientos válidos
    moveMade = False  # Bandera para indicar si se ha realizado un movimiento
    animate = False  # Bandera para indicar si se debe animar un movimiento
    loadImages()  # Carga las imágenes de las piezas
    running = True  # Bandera para mantener el juego en ejecución
    sqSelected = ()  # Almacena la casilla seleccionada (fila, columna)
    playerClicks = []  # Lista de clics del jugador (para seleccionar piezas y movimientos)
    gameOver = False  # Bandera para indicar si el juego ha terminado
    playerOne = True  # True si el jugador 1 es humano, False si es IA
    playerTwo = False  # True si el jugador 2 es humano, False si es IA

    # Bucle principal del juego
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)  # Determina si es el turno de un jugador humano

        # Manejo de eventos
        for e in p.event.get():
            if e.type == p.QUIT:  # Si el usuario cierra la ventana
                running = False  # Detiene el bucle del juego
            elif e.type == p.MOUSEBUTTONDOWN:  # Si el usuario hace clic con el ratón
                if not gameOver and humanTurn:  # Si el juego no ha terminado y es el turno del jugador humano
                    location = p.mouse.get_pos()  # Obtiene la posición del ratón
                    col = location[0] // SQ_SIZE  # Calcula la columna del tablero
                    row = location[1] // SQ_SIZE  # Calcula la fila del tablero
                    if sqSelected == (row, col):  # Si la casilla ya está seleccionada
                        sqSelected = ()  # Deselecciona la casilla
                        playerClicks = []  # Limpia la lista de clics
                    else:
                        sqSelected = (row, col)  # Almacena la casilla seleccionada
                        playerClicks.append(sqSelected)  # Añade la casilla a la lista de clics
                    if len(playerClicks) == 2:  # Si el jugador ha seleccionado dos casillas
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)  # Crea un movimiento
                        #print(move.getChessNotation())  # Imprime la notación del movimiento
                        for i in range(len(validMoves)):  # Verifica si el movimiento es válido
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])  # Realiza el movimiento
                                moveMade = True  # Indica que se ha realizado un movimiento
                                animate = True  # Indica que se debe animar el movimiento
                                sqSelected = ()  # Limpia la selección
                                playerClicks = []  # Limpia la lista de clics
                        if not moveMade:  # Si el movimiento no es válido
                            playerClicks = [sqSelected]  # Mantiene la selección de la pieza
            elif e.type == p.KEYDOWN:  # Si el usuario presiona una tecla
                if e.key == p.K_z:  # Si la tecla es 'z' (deshacer)
                    gs.undoMove()  # Deshace el último movimiento
                    moveMade = True  # Indica que se ha realizado un cambio
                    animate = False  # No se anima el deshacer
                    gameOver = False  # El juego no ha terminado
                if e.key == p.K_r:  # Si la tecla es 'r' (reiniciar)
                    gs = ChessEngine.GameState()  # Reinicia el estado del juego
                    validMoves = gs.getValidMoves()  # Obtiene los movimientos válidos
                    sqSelected = ()  # Limpia la selección
                    playerClicks = []  # Limpia la lista de clics
                    moveMade = False  # Indica que no se ha realizado un movimiento
                    animate = False  # No se anima el reinicio
                    gameOver = False  # El juego no ha terminado

        # Turno de la IA
        if not gameOver and not humanTurn:
            AIMove = SmartMoveFinder.findBestMove(gs, validMoves)  # Encuentra el mejor movimiento
            if AIMove is None:  # Si no hay un mejor movimiento
                AIMove = SmartMoveFinder.findRandomMove(validMoves)  # Encuentra un movimiento aleatorio
            gs.makeMove(AIMove)  # Realiza el movimiento de la IA
            moveMade = True  # Indica que se ha realizado un movimiento
            animate = True  # Indica que se debe animar el movimiento

        # Actualización del estado del juego
        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)  # Anima el movimiento
            validMoves = gs.getValidMoves()  # Obtiene los nuevos movimientos válidos
            moveMade = False  # Reinicia la bandera de movimiento
            animate = False  # Reinicia la bandera de animación
        drawGameState(screen, gs, validMoves, sqSelected)  # Dibuja el estado del juego
        if gs.checkMate:  # Si hay jaque mate
            gameOver = True  # El juego ha terminado
            if gs.whiteToMove:  # Si es el turno de las blancas
                drawText(screen, "Black wins by checkmate")  # Las negras ganan
            else:
                drawText(screen, "White wins by checkmate")  # Las blancas ganan
        elif gs.staleMate:  # Si hay empate
            gameOver = True  # El juego ha terminado
            drawText(screen, "Stalemate")  # Muestra el mensaje de empate
        clock.tick(MAX_FPS)  # Controla la velocidad de fotogramas
        p.display.flip()  # Actualiza la pantalla

# Función para resaltar las casillas seleccionadas y los movimientos válidos
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():  # Si hay una casilla seleccionada
        r, c = sqSelected  # Obtiene la fila y columna de la casilla
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):  # Si la pieza es del jugador actual
            s = p.Surface((SQ_SIZE, SQ_SIZE))  # Crea una superficie para resaltar
            s.set_alpha(100)  # Establece la transparencia
            s.fill(p.Color('blue'))  # Rellena con color azul
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))  # Dibuja el resaltado en la casilla seleccionada
            s.fill(p.Color('yellow'))  # Cambia el color para los movimientos válidos
            for move in validMoves:  # Resalta los movimientos válidos
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

# Función para dibujar el estado del juego
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)  # Dibuja el tablero
    highlightSquares(screen, gs, validMoves, sqSelected)  # Resalta las casillas seleccionadas
    drawPieces(screen, gs.board)  # Dibuja las piezas

# Función para dibujar el tablero
def drawBoard(screen):
    colors = [p.Color("white"), p.Color("darkgray")]  # Colores del tablero
    for r in range(DIMENSION):  # Recorre las filas
        for c in range(DIMENSION):  # Recorre las columnas
            color = colors[((r + c) % 2)]  # Alterna los colores
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))  # Dibuja la casilla

# Función para dibujar las piezas
def drawPieces(screen, board):
    for r in range(DIMENSION):  # Recorre las filas
        for c in range(DIMENSION):  # Recorre las columnas
            piece = board[r][c]  # Obtiene la pieza en la casilla
            if piece != "--":  # Si la casilla no está vacía
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))  # Dibuja la pieza

# Función para animar los movimientos
def animateMove(move, screen, board, clock):
    colors = [p.Color("white"), p.Color("darkgray")]  # Colores del tablero
    dR = move.endRow - move.startRow  # Diferencia en filas
    dC = move.endCol - move.startCol  # Diferencia en columnas
    framesPerSquare = 10  # Fotogramas por casilla
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare  # Total de fotogramas para la animación
    for frame in range(frameCount + 1):  # Recorre los fotogramas
        r, c = ((move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount))  # Calcula la posición intermedia
        drawBoard(screen)  # Dibuja el tablero
        drawPieces(screen, board)  # Dibuja las piezas
        color = colors[(move.endRow + move.endCol) % 2]  # Color de la casilla de destino
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)  # Casilla de destino
        p.draw.rect(screen, color, endSquare)  # Dibuja la casilla de destino
        if move.pieceCaptured != '--':  # Si hay una pieza capturada
            screen.blit(IMAGES[move.pieceCaptured], endSquare)  # Dibuja la pieza capturada
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))  # Dibuja la pieza movida
        p.display.flip()  # Actualiza la pantalla
        clock.tick(60)  # Controla la velocidad de la animación

# Función para dibujar texto en la pantalla
def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)  # Fuente del texto
    textObject = font.render(text, 0, p.Color('Black'))  # Renderiza el texto
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2, HEIGHT / 2 - textObject.get_height() / 2)  # Centra el texto
    screen.blit(textObject, textLocation)  # Dibuja el texto en la pantalla

# Ejecución del juego
if __name__ == "__main__":
    main()  # Llama a la función principal