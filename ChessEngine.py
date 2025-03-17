class GameState():
    def __init__(self):
        """
        Inicializa el estado del juego con el tablero en su posición inicial.
        """
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],  # Fila 0: Piezas negras
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],  # Fila 1: Peones negros
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # Filas 2-5: Vacías
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],  # Fila 6: Peones blancos
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]   # Fila 7: Piezas blancas
        ]

        # Diccionario que mapea cada tipo de pieza a su función de movimiento correspondiente.
        self.moveFunctions = {"p": self.getPawnMoves, "R": self.getRookMoves, "N": self.getKnightMoves,
                              "B": self.getBishopMoves, "Q": self.getQueenMoves, "K": self.getKingMoves}

        self.whiteToMove = True  # True si es el turno de las blancas, False si es el turno de las negras.
        self.moveLog = []  # Lista para almacenar los movimientos realizados.
        self.whiteKingLocation = (7, 4)  # Ubicación inicial del rey blanco.
        self.blackKingLocation = (0, 4)  # Ubicación inicial del rey negro.
        self.checkMate = False  # True si hay jaque mate.
        self.staleMate = False  # True si hay empate.
        self.enpassantPossible = ()  # Coordenadas de la casilla donde se puede realizar una captura al paso.
        self.currentCastlingRight = CastleRights(True, True, True, True)  # Derechos de enroque actuales.
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]  # Historial de derechos de enroque.

    def makeMove(self, move):
        """
        Realiza un movimiento en el tablero.
        :param move: Objeto Move que representa el movimiento a realizar.
        """
        self.board[move.startRow][move.startCol] = "--"  # Vacía la casilla de origen.
        self.board[move.endRow][move.endCol] = move.pieceMoved  # Coloca la pieza en la casilla de destino.
        self.moveLog.append(move)  # Añade el movimiento al registro.
        self.whiteToMove = not self.whiteToMove  # Cambia el turno.

        # Actualiza la ubicación del rey si se mueve.
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        # Promoción de peón.
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"  # Convierte el peón en reina.

        # Captura al paso.
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"  # Elimina el peón capturado.

        # Actualiza la posibilidad de captura al paso.
        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        # Movimiento de enroque.
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # Enroque corto.
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = "--"
            else:  # Enroque largo.
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = "--"

        # Actualiza los derechos de enroque y guarda el estado actual en el historial.
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
                                                self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    def updateCastleRights(self, move):
        """
        Actualiza los derechos de enroque basados en el movimiento realizado.
        :param move: Objeto Move que representa el movimiento realizado.
        """
        if move.pieceMoved == "wK":  # Si el rey blanco se mueve, pierde derechos de enroque.
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == "bK":  # Si el rey negro se mueve, pierde derechos de enroque.
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == "wR":  # Si una torre blanca se mueve, pierde derechos de enroque.
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == "bR":  # Si una torre negra se mueve, pierde derechos de enroque.
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False

    def undoMove(self):
        """
        Deshace el último movimiento realizado.
        """
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()  # Obtiene el último movimiento.
            self.board[move.startRow][move.startCol] = move.pieceMoved  # Restaura la pieza movida.
            self.board[move.endRow][move.endCol] = move.pieceCaptured  # Restaura la pieza capturada.
            self.whiteToMove = not self.whiteToMove  # Cambia el turno.

            # Restaura la ubicación del rey si se movió.
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            # Restaura la captura al paso.
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"  # Elimina el peón movido.
                self.board[move.startRow][move.endCol] = move.pieceCaptured  # Restaura el peón capturado.
                self.enpassantPossible = (move.endRow, move.endCol)

            # Restaura la posibilidad de captura al paso.
            if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

            # Restaura los derechos de enroque.
            self.castleRightsLog.pop()  # Elimina el último estado de derechos de enroque.
            newRights = self.castleRightsLog[-1]  # Obtiene el estado anterior.
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)

            # Restaura el movimiento de enroque.
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # Enroque corto.
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else:  # Enroque largo.
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"

            # Restaura el estado de jaque mate y empate.
            self.checkMate = False
            self.staleMate = False

    def getValidMoves(self):
        """
        Obtiene todos los movimientos válidos para el jugador actual.
        :return: Lista de movimientos válidos.
        """
        tempEnpassantPossible = self.enpassantPossible  # Guarda el estado actual de la captura al paso.
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
                                       self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)  # Guarda los derechos de enroque actuales.
        moves = self.getAllPossibleMoves()  # Obtiene todos los movimientos posibles.

        # Añade movimientos de enroque si es posible.
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        # Filtra los movimientos que dejan al rey en jaque.
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])  # Realiza el movimiento.
            self.whiteToMove = not self.whiteToMove  # Cambia el turno.
            if self.inCheck():  # Verifica si el rey está en jaque.
                moves.remove(moves[i])  # Elimina el movimiento si deja al rey en jaque.
            self.whiteToMove = not self.whiteToMove  # Restaura el turno.
            self.undoMove()  # Deshace el movimiento.

        # Verifica si el juego ha terminado en jaque mate o empate.
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True  # Jaque mate.
            else:
                self.staleMate = True  # Empate.
        else:
            self.checkMate = False
            self.staleMate = False

        # Restaura el estado de la captura al paso y los derechos de enroque.
        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves

    def inCheck(self):
        """
        Verifica si el rey del jugador actual está en jaque.
        :return: True si el rey está en jaque, False en caso contrario.
        """
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])  # Rey blanco.
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])  # Rey negro.

    def squareUnderAttack(self, r, c):
        """
        Verifica si una casilla está bajo ataque por el oponente.
        :param r: Fila de la casilla.
        :param c: Columna de la casilla.
        :return: True si la casilla está bajo ataque, False en caso contrario.
        """
        self.whiteToMove = not self.whiteToMove  # Cambia el turno para obtener los movimientos del oponente.
        oppMoves = self.getAllPossibleMoves()  # Obtiene los movimientos del oponente.
        self.whiteToMove = not self.whiteToMove  # Restaura el turno.
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:  # Si la casilla está bajo ataque.
                return True
        return False

    def getAllPossibleMoves(self):
        """
        Obtiene todos los movimientos posibles para el jugador actual.
        :return: Lista de movimientos posibles.
        """
        moves = []
        for r in range(len(self.board)):  # Recorre las filas del tablero.
            for c in range(len(self.board[r])):  # Recorre las columnas del tablero.
                turn = self.board[r][c][0]  # Obtiene el color de la pieza.
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):  # Verifica si es el turno de la pieza.
                    piece = self.board[r][c][1]  # Obtiene el tipo de pieza.
                    self.moveFunctions[piece](r, c, moves)  # Llama a la función de movimiento correspondiente.
        return moves

    def getPawnMoves(self, r, c, moves):
        """
        Obtiene todos los movimientos posibles para un peón.
        :param r: Fila del peón.
        :param c: Columna del peón.
        :param moves: Lista de movimientos.
        """
        if self.whiteToMove:  # Movimientos para peones blancos.
            if self.board[r - 1][c] == "--":  # Movimiento hacia adelante.
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":  # Movimiento inicial de dos casillas.
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:  # Captura a la izquierda.
                if self.board[r - 1][c - 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible:  # Captura al paso.
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:  # Captura a la derecha.
                if self.board[r - 1][c + 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:  # Captura al paso.
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))
        else:  # Movimientos para peones negros.
            if self.board[r + 1][c] == "--":  # Movimiento hacia adelante.
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":  # Movimiento inicial de dos casillas.
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:  # Captura a la izquierda.
                if self.board[r + 1][c - 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:  # Captura al paso.
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:  # Captura a la derecha.
                if self.board[r + 1][c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:  # Captura al paso.
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))

    def getRookMoves(self, r, c, moves):
        """
        Obtiene todos los movimientos posibles para una torre.
        :param r: Fila de la torre.
        :param c: Columna de la torre.
        :param moves: Lista de movimientos.
        """
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # Direcciones posibles: arriba, izquierda, abajo, derecha.
        enemyColor = "b" if self.whiteToMove else "w"  # Color del oponente.
        for d in directions:
            for i in range(1, 8):  # Recorre hasta 7 casillas en cada dirección.
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # Verifica que la casilla esté dentro del tablero.
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # Casilla vacía.
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # Captura de pieza enemiga.
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # Pieza aliada, no se puede mover más en esta dirección.
                        break
                else:  # Fuera del tablero.
                    break

    def getKnightMoves(self, r, c, moves):
        """
        Obtiene todos los movimientos posibles para un caballo.
        :param r: Fila del caballo.
        :param c: Columna del caballo.
        :param moves: Lista de movimientos.
        """
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1))  # Movimientos en L.
        allyColor = "w" if self.whiteToMove else "b"  # Color del aliado.
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # Verifica que la casilla esté dentro del tablero.
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # Si no es una pieza aliada.
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves):
        """
        Obtiene todos los movimientos posibles para un alfil.
        :param r: Fila del alfil.
        :param c: Columna del alfil.
        :param moves: Lista de movimientos.
        """
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # Direcciones diagonales.
        enemyColor = "b" if self.whiteToMove else "w"  # Color del oponente.
        for d in directions:
            for i in range(1, 8):  # Recorre hasta 7 casillas en cada dirección.
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # Verifica que la casilla esté dentro del tablero.
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # Casilla vacía.
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # Captura de pieza enemiga.
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # Pieza aliada, no se puede mover más en esta dirección.
                        break
                else:  # Fuera del tablero.
                    break

    def getQueenMoves(self, r, c, moves):
        """
        Obtiene todos los movimientos posibles para una reina.
        :param r: Fila de la reina.
        :param c: Columna de la reina.
        :param moves: Lista de movimientos.
        """
        self.getRookMoves(r, c, moves)  # Movimientos de torre.
        self.getBishopMoves(r, c, moves)  # Movimientos de alfil.

    def getKingMoves(self, r, c, moves):
        """
        Obtiene todos los movimientos posibles para un rey.
        :param r: Fila del rey.
        :param c: Columna del rey.
        :param moves: Lista de movimientos.
        """
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1),
                        (0, 1), (1, -1), (1, 0), (1, 1))  # Movimientos en todas las direcciones.
        allyColor = "w" if self.whiteToMove else "b"  # Color del aliado.
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # Verifica que la casilla esté dentro del tablero.
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # Si no es una pieza aliada.
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getCastleMoves(self, r, c, moves):
        """
        Obtiene todos los movimientos de enroque posibles.
        :param r: Fila del rey.
        :param c: Columna del rey.
        :param moves: Lista de movimientos.
        """
        if self.squareUnderAttack(r, c):  # Si el rey está en jaque, no puede enrocar.
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)  # Enroque corto.
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)  # Enroque largo.

    def getKingsideCastleMoves(self, r, c, moves):
        """
        Obtiene los movimientos de enroque corto.
        :param r: Fila del rey.
        :param c: Columna del rey.
        :param moves: Lista de movimientos.
        """
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":  # Verifica que las casillas estén vacías.
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):  # Verifica que no estén bajo ataque.
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))  # Añade el movimiento de enroque.

    def getQueensideCastleMoves(self, r, c, moves):
        """
        Obtiene los movimientos de enroque largo.
        :param r: Fila del rey.
        :param c: Columna del rey.
        :param moves: Lista de movimientos.
        """
        if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":  # Verifica que las casillas estén vacías.
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):  # Verifica que no estén bajo ataque.
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))  # Añade el movimiento de enroque.


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        """
        Inicializa los derechos de enroque.
        :param wks: Enroque corto para las blancas.
        :param bks: Enroque corto para las negras.
        :param wqs: Enroque largo para las blancas.
        :param bqs: Enroque largo para las negras.
        """
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    """
    Clase para representar un movimiento en el ajedrez.
    """
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}  # Mapeo de filas a números.
    rowsToRanks = {v: k for k, v in ranksToRows.items()}  # Mapeo inverso de filas a números.
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}  # Mapeo de columnas a letras.
    colsToFiles = {v: k for k, v in filesToCols.items()}  # Mapeo inverso de columnas a letras.

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        """
        Inicializa un movimiento.
        :param startSq: Casilla de inicio (fila, columna).
        :param endSq: Casilla de destino (fila, columna).
        :param board: Tablero actual.
        :param isEnpassantMove: True si es una captura al paso.
        :param isCastleMove: True si es un enroque.
        """
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]  # Pieza movida.
        self.pieceCaptured = board[self.endRow][self.endCol]  # Pieza capturada.
        self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7)  # Promoción de peón.
        self.isEnpassantMove = isEnpassantMove  # Captura al paso.
        if self.isEnpassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"  # Pieza capturada en captura al paso.
        self.isCastleMove = isCastleMove  # Enroque.
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol  # ID único del movimiento.

    def __eq__(self, other):
        """
        Compara dos movimientos por su ID.
        :param other: Otro movimiento.
        :return: True si los movimientos son iguales, False en caso contrario.
        """
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        """
        Obtiene la notación algebraica del movimiento.
        :return: Notación algebraica (e.g., "e2e4").
        """
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        """
        Convierte filas y columnas en notación algebraica.
        :param r: Fila.
        :param c: Columna.
        :return: Notación algebraica (e.g., "e2").
        """
        return self.colsToFiles[c] + self.rowsToRanks[r]