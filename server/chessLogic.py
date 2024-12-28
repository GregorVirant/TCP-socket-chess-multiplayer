
from enum import Enum
import copy
# razred za vzdrževanje igre

class BoardType(Enum):
    STANDARD = 0




class ChessBoard:

    #boardSize=8

    def __init__(self, bType):
        self.startBoard = self._setBoard(bType)
        self.currBoard = self.startBoard
        self.isWhiteToMove = True
        self.enPassantSquare = []
        self.moves = []
        self.castlingOptions = [True, True, True, True] #KQkq
        self.halfMoves = (0,0) #polpoteze od zadnjega ujetja ali premika kmeta
        self.boardSize=8


    def getBoard(self):
        return self.currBoard
    
    def getStartBoard(self):
        return self.startBoard
    
    def _isCastlingLegal(self, king_start, rook_start, king_end):
            # Preveri, če se kralj ali trdnjava še nista premaknila
            if self.isWhiteToMove:
                if king_start[1] == 4 and rook_start[1] == 7 and not self.castlingOptions[0]: #K
                    return False
                if king_start[1] == 4 and rook_start[1] == 0 and not self.castlingOptions[1]: #Q
                    return False
            else:
                if king_start[1] == 4 and rook_start[1] == 7 and not self.castlingOptions[2]: #k
                    return False
                if king_start[1] == 4 and rook_start[1] == 0 and not self.castlingOptions[3]: #q
                    return False
                
            # Preveri, če ni figur med kraljem in trdnjavo
            if rook_start[1] > king_start[1]:
                step = 1 # desno
            else:
                step = -1 # levo
            for col in range(king_start[1] + step, rook_start[1], step):
                if self.currBoard[king_start[0]][col] != 0:
                    return False
            
            # Preveri, če kralj ni pod napadom med premikom
            for col in range(king_start[1], king_end[1] + step, step):
                if self._isUnderAttack(king_start[0], col):
                    return False
            
            return True
    
    def _isMoveLegalNoCheckAfterMove(self,row,column,targetRow,targetColumn):
        board = []
        for row1 in self.currBoard:
            newRow=[]
            for element in row1:
                newRow.append(element)
            board.append(newRow)

        self.currBoard[targetRow][targetColumn]=self.currBoard[row][column]
        self.currBoard[row][column]=0
        if self.isCheck(self.isWhiteToMove):
            self.currBoard = board
            return False
        self.currBoard = board
        return True

    def _findCurrentlySelected(self,legalMoves):
        for row in range(8):
            for column in range(8):
                if legalMoves[row][column] == 1:
                    return (row, column)
        return (None,None)

    def _areMovesLegalNoCheckAfterMove(self,legalMoves):
        row,column = self._findCurrentlySelected(legalMoves)
        if row == None:
            print("No piece selected.")
        
        for rowT in range(8):
            for columnT in range(8):
                if legalMoves[rowT][columnT]>1:
                    if not self._isMoveLegalNoCheckAfterMove(row,column, rowT, columnT):
                        legalMoves[rowT][columnT] = 0

    def getLegalMoves(self, row, column, checkForCheck = True):
        legalMoves = self._getEmptyBoard()
        
        if(not (self.isWhiteToMove and self.currBoard[row][column] > 0 or not self.isWhiteToMove and self.currBoard[row][column] < 0)):
            return legalMoves

        self._calculateLegalMoves(row, column, legalMoves)

        if checkForCheck:
            self._areMovesLegalNoCheckAfterMove(legalMoves)

        return legalMoves

    
    def makeMove(self, originSquare, newSquare): #originSquare and newSquare sta toupla ki vsebujeta koordinati x in y
        legalMoves =  self.getLegalMoves(originSquare[0], originSquare[1])
        if(legalMoves[newSquare[0]][newSquare[1]] < 2):
            print("Move is not legal")
            return False
        
        piece = self.currBoard[originSquare[0]][originSquare[1]]

        # Preveri legalnost rokade
        if abs(piece) == 6:
            if newSquare == (originSquare[0], originSquare[1] + 2):  # Kingside rokada
                if not self._isCastlingLegal(originSquare, (originSquare[0], 7), newSquare):
                    return False
                # Premakni trdnjavo
                self.currBoard[originSquare[0]][5] = self.currBoard[originSquare[0]][7]
                self.currBoard[originSquare[0]][7] = 0
            elif newSquare == (originSquare[0], originSquare[1] - 2):  # Queenside rokada
                if not self._isCastlingLegal(originSquare, (originSquare[0], 0), newSquare):
                    return False
                # Premakni trdnjavo
                self.currBoard[originSquare[0]][3] = self.currBoard[originSquare[0]][0]
                self.currBoard[originSquare[0]][0] = 0
        
        # Posodobi premike kralja in trdnjave
        if (abs(piece) == 6):
            if self.isWhiteToMove:
                self.castlingOptions[0] = False
                self.castlingOptions[1] = False
            else:
                self.castlingOptions[2] = False
                self.castlingOptions[3] = False
        elif (abs(piece) == 2):
            if self.isWhiteToMove:
                if originSquare[1] == 0:
                    self.castlingOptions[1] = False
                elif originSquare[1] == 7:
                    self.castlingOptions[0] = False
            else:
                if originSquare[1] == 0:
                    self.castlingOptions[3] = False
                elif originSquare[1] == 7:
                    self.castlingOptions[2] = False

        self.isWhiteToMove = not self.isWhiteToMove
        # izvedem potezo
        
        if(abs(piece) == 1 and self.enPassantSquare == [newSquare[0], newSquare[1]]):
            self.currBoard[originSquare[0]][newSquare[1]] = 0
        self.currBoard[newSquare[0]][newSquare[1]] = self.currBoard[originSquare[0]][originSquare[1]]
        self.currBoard[originSquare[0]][originSquare[1]] = 0
        #preverim ostale spremenljivke

        #preverjanje en passant
        if(abs(piece) == 1 and abs(originSquare[0] - newSquare[0]) == 2):
           
            # nastavim polje
           
            self.enPassantSquare=[int((originSquare[0] + newSquare[0]) / 2), newSquare[1]]
        else:
            self.enPassantSquare=[]
        # polpoteze od zadnjega premika kmeta ali ujetja
        if(legalMoves == 2):
            if(self.isWhiteToMove):
                self.halfMoves[0] += 1
            else:
                self.halfMoves[1] += 1
        else:
            self.halfMoves = (0,0)
        self.moves.append([(originSquare),(newSquare)])
        return True
        #castling TODO

    def _setBoard(self, bType): #_ pomeni da je metoda privatna
        match(bType):
            case 0:
                return [[-2,-3,-4,-5,-6,-4,-3,-2],
                        [-1,-1,-1,-1,-1,-1,-1,-1],
                        [0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0],
                        [1,1,1,1,1,1,1,1],
                        [2,3,4,5,6,4,3,2]]
            case _:#default
                return [[-2,-3,-4,-5,-6,-4,-3,-2],
                        [-1,-1,-1,-1,-1,-1,-1,-1],
                        [0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0],
                        [1,1,1,1,1,1,1,1],
                        [2,3,4,5,6,4,3,2]]
    

    def _getEmptyBoard(self):
        emptyBoard = copy.deepcopy(self.currBoard)
        for i in range(len(emptyBoard)):
            for j in range(len(emptyBoard[i])):
                emptyBoard[i][j] = 0
        return emptyBoard

    
    def _isLegal(self, row, column):
        if row < 0 or row > self.boardSize-1 or column < 0 or self.boardSize-1 < column: 
            return False
        return self.currBoard[row][column] == 0

    def _isLegalTake(self, row, column):
        if row < 0 or row > self.boardSize-1 or column < 0 or self.boardSize-1 <column: 
            return False
    
        if self.isWhiteToMove and self.currBoard[row][column] >= 0:
            return False
        if (not self.isWhiteToMove) and self.currBoard[row][column] <= 0:
            return False
        return True
    
    def _isUnderAttack(self, row, column):
        originalTurn = self.isWhiteToMove
        self.isWhiteToMove = not self.isWhiteToMove  # Obrnemo vrednost
        for i in range(self.boardSize):
            for j in range(self.boardSize):
                piece = self.currBoard[i][j]
                if (self.isWhiteToMove and piece > 0) or (not self.isWhiteToMove and piece < 0):
                    legalMoves = self._getEmptyBoard()
                    legalMoves = self.getLegalMoves(i, j, checkForCheck=False)
                    if legalMoves[row][column] != 0:
                        self.isWhiteToMove = originalTurn  # Povrnemo originalno vrednost
                        return True
        self.isWhiteToMove = originalTurn  # Povrnemo originalno vrednost
        return False
    
    def isCheck(self, isWhite):
        for i in range(self.boardSize):
            for j in range(self.boardSize):
                piece = self.currBoard[i][j]
                if (isWhite and piece == 6) or (not isWhite and piece == -6):
                    if self._isUnderAttack(i, j):
                        return True
        return False
    def _legalMovesPawn(self,row,column,legalMoves):
        #nastavim barvo
        if self.currBoard[row][column] > 0:
            color = -1
        else:
            color = 1
        
        # premik za 1 naprej
        if self._isLegal(row + color, column):
            legalMoves[row + color][column] = 2
            # premik za 2 iz osnovnega polja
            if (row == 6 and self._isLegal(row - 2, column) and color == -1) or (row == 1 and self._isLegal(row + 2, column) and color == 1): #dvojna poteza
                legalMoves[row + color * 2][column] = 2
        # ujem figure v eno stran
        if self._isLegalTake(row + color, column + color) or self.enPassantSquare == [row + color, column + color]: # ujem figure s kmetom ali en passant
            legalMoves[row + color][column + color] = 3
        # ujem figure v drugo stran
        if self._isLegalTake(row + color, column - color) or self.enPassantSquare == [row + color, column - color]: #ujem figure ali en-passant
            legalMoves[row + color][column - color] = 3

    def _legalMovesBishop(self,row, column, legalMoves):
        # če je beli True sicer false
        if self.currBoard[row][column] > 0:
            color = True
        else:
            color=False
        vectors = [(1, 1), (1, -1), (-1, 1), (-1, -1)] # določimo smeri premika
        for i in range(4):
            a = vectors[i][0]
            b = vectors[i][1]
        
            for j in range(1,7):
                if self._isLegal(row + j * a, column + j * b):
                    legalMoves[row + j * a][column + j * b] = 2    
                elif self._isLegalTake(row + j * a, column + j * b):
                    legalMoves[row + j * a][column + j * b] = 3
                    break
                else:
                    break    
    def _legalMovesKnight(self, row, column, legalMoves):
        vectors = [(2,1), (2,-1), (-2,1), (-2,-1), (1,2), (1,-2), (-1,2), (-1,-2)]
        if(self.currBoard[row][column] > 0):
            color = True
        else:
            color = False

        for i in range(8):
            moveRow = vectors[i][0]
            moveColumn = vectors[i][1]
            if self._isLegal(row + moveRow, column + moveColumn):
                legalMoves[row + moveRow][column + moveColumn] = 2
            elif self._isLegalTake(row + moveRow, column + moveColumn):
                legalMoves[row + moveRow][column + moveColumn] = 3
    def _legalMovesRook(self,row, column,legalMoves):
        if self.currBoard[row][column] > 0:
            color = True
        else:
            color=False
        vectors = [(0,1), (0,-1), (1,0), (-1,0)]

        for i in range(4):
            moveRow = vectors[i][0]
            moveColumn = vectors[i][1]
            for j in range(1,8):
                if self._isLegal(row + j * moveRow, column + j * moveColumn):
                    legalMoves[row + j * moveRow][column + j * moveColumn] = 2
                elif self._isLegalTake(row + j * moveRow, column + j * moveColumn):
                    legalMoves[row + j * moveRow][column + j * moveColumn] = 3
                    break
                else:
                    break
    def _legalMovesKing(self, row, column, legalMoves):
        if self.currBoard[row][column] > 0:
            color = True
        else:
            color = False
        
        vectors = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
        for i in vectors:
            moveRow = i[0]
            moveColumn = i[1]
            if self._isLegal(row + moveRow, column + moveColumn):
                legalMoves[row + moveRow][column + moveColumn] = 2
            elif self._isLegalTake(row + moveRow, column + moveColumn):
                legalMoves[row + moveRow][column + moveColumn] = 3

        # Preveri rokado na kraljevi strani
        if color and self.currBoard[row][column] == 6:  # Beli kralj
            if self.castlingOptions[0] and self._isCastlingLegal((row, column), (row, 7), (row, column + 2)):
                legalMoves[row][column + 2] = 2
            if self.castlingOptions[1] and self._isCastlingLegal((row, column), (row, 0), (row, column - 2)):
                legalMoves[row][column - 2] = 2
        elif not color and self.currBoard[row][column] == -6:  # Črni kralj
            if self.castlingOptions[2] and self._isCastlingLegal((row, column), (row, 7), (row, column + 2)):
                legalMoves[row][column + 2] = 2
            if self.castlingOptions[3] and self._isCastlingLegal((row, column), (row, 0), (row, column - 2)):
                legalMoves[row][column - 2] = 2


    def _calculateLegalMoves(self, row,column,legalMoves):
        if(self.isWhiteToMove and self.currBoard[row][column] > 0 or (not self.isWhiteToMove and self.currBoard[row][column] < 0)):
            
            legalMoves[row][column] = 1
            if self.currBoard[row][column] == 0:
                return
            piece = abs(self.currBoard[row][column])
            
            if piece == 1: # kmet
                #legalMovesPawn(row,column,board,legalMoves)
                self._legalMovesPawn(row,column,legalMoves)
                return

            if piece == 2: # trdnjava
                self._legalMovesRook(row,column,legalMoves)
                return
            
            if piece == 3: # skakač
                self._legalMovesKnight(row,column,legalMoves)
                return
            
            if piece == 4: # tekač
                self._legalMovesBishop(row,column,legalMoves)
                return

            if piece == 5: # kraljica je kombinacija trdnjave in tekača
                self._legalMovesBishop(row,column,legalMoves)
                self._legalMovesRook(row,column,legalMoves)
                return

            if piece == 6: # kralj
                self._legalMovesKing(row,column,legalMoves)
                return
#end of class





    
# def move(pieceRow,pieceColumn,clickedRow,clickedColumn,board):
#     board[clickedRow][clickedColumn]=board[pieceRow][pieceColumn]
#     board[pieceRow][pieceColumn]=0

