import chessLogic
import random
import time
import os

class Game:
    #GAME ID JE SAMO POZICIJA KI JE V ARRAYI
    def __init__(self, gameID,socketC1,uniqueCodeC1):
        self.start = False

        self.gameID = gameID
        self.socketC1 = socketC1
        self.uniqueCodeC1 = uniqueCodeC1
        self.socketC2 = None
        self.uniqueCodeC2 = None

        self.chess = chessLogic.ChessBoard(0)

        self.whoIsWhite = random.randint(1, 2)
        self.chessBoard = self.chess.currBoard
        self.isWhiteTurn = True

        self.moves = []
        
        self.turnNumber = 0

        self.timeWhite = 600  # 10 minutes in seconds
        self.timeBlack = 600  # 10 minutes in seconds
        self.lastMoveTime = time.time()
        
        self.fileName = f"game{self.gameID}.txt"

        self.isRunning = True

    def isPlayerTurn(self, uniqueId):
        if self.whoIsWhite == 1:
            return (uniqueId == self.uniqueCodeC1 and self.isWhiteTurn) or (uniqueId == self.uniqueCodeC2 and not self.isWhiteTurn)
        else:
            return (uniqueId == self.uniqueCodeC1 and not self.isWhiteTurn) or (uniqueId == self.uniqueCodeC2 and self.isWhiteTurn)
    
    def updateBoard(self):
        self.chessBoard = self.chess.currBoard

    def _updateTime(self):
        if self.turnNumber == 0:
            self.lastMoveTime = time.time()
            return  # Don't update time on the first move
        currentTime = time.time()
        timeElapsed = currentTime - self.lastMoveTime
        self.lastMoveTime = currentTime
        if self.isWhiteTurn:
            self.timeWhite -= timeElapsed
        else:
            self.timeBlack -= timeElapsed

    def makeMove(self, odlSquare, newSquare):
        moveMade = self.chess.makeMove(odlSquare, newSquare)
        if not moveMade:
            return False
        self.updateBoard()
        self._updateTime()
        self.isWhiteTurn = not self.isWhiteTurn
        self.turnNumber += 1
        return moveMade
        
    def isAlreadyInGame(self,uniqueCode,socket): #ce je bil disconectan pa se na novo joina
        #ce je uniqueCode enak uniqueCodeC1 al uniqueCodeC2
            #self.socketC1/C2 = socket
            #return True
        #return False
        pass

    def isPlayerReconnecting(self, unique_id):
        return (self.uniqueCodeC1 == unique_id and self.socketC1 is None) or (self.uniqueCodeC2 == unique_id and self.socketC2 is None)

    def reconnectPlayer(self, conn, unique_id):
        if self.uniqueCodeC1 == unique_id:
            self.socketC1 = conn
        elif self.uniqueCodeC2 == unique_id:
            self.socketC2 = conn
    def addPlayer2(self,conn,unique_id):
        self.socketC2 = conn
        self.uniqueCodeC2 = unique_id
    
    def disconnectPlayer(self,unique_id):
        #print(f"Zahteva za izhod iz igre {self.gameID} od igralca {unique_id}")
        if self.uniqueCodeC1 == unique_id:
            if self.socketC1:
                self.socketC1.close()
            self.socketC1 = None
        elif self.uniqueCodeC2 == unique_id:
            if self.socketC2:
                self.socketC2.close()
            self.socketC2 = None

    def isOneSpaceEmpty(self): #ce se ni not gledamo ce slucajno se igra fraj
        return self.uniqueCodeC2 == None or self.uniqueCodeC1 == None #CE JE None JE SE PRAZNO
    
    def isEmpty(self):
        return self.socketC1 is None and self.socketC2 is None
    
    def flipBoard(self):
        return [row[::-1] for row in self.chessBoard[::-1]]
    
    def flipLegalMoves(self,legalMoves):
        return [row[::-1] for row in legalMoves[::-1]]
    
    def getPlayerNumber(self, unique_id):
        if self.uniqueCodeC1 == unique_id:
            return 1
        elif self.uniqueCodeC2 == unique_id:
            return 2
        return None

    def coordsToAlgebraic(self, row, col):
        files = 'abcdefgh'
        ranks = '87654321'
        return f"{files[col]}{ranks[row]}"
    
    def getLegalMoves(self, row, col):
        return self.chess.getLegalMoves(row, col)
    
    def isAmbiguousMove(self, oldRow, oldCol, newRow, newCol):
        try:
            piece = self.chess.currBoard[oldRow][oldCol]
            if abs(piece) in (1, 4, 6):
                return False
            #poisce vse figure istega tipa
            pieces = []
            for i in range(8):
                for j in range(8):
                    if self.chess.currBoard[i][j] == piece:
                        pieces.append((i, j))
            #ce je samo ena figura tega tipa
            if len(pieces) == 1:
                return False
            #ce je vec figur istega tipa in pogleda če se lahko druga figura prestavi na isto mesto
            needRow = ""
            needCol = ""
            for p in pieces:
                if p == (oldRow, oldCol):
                    continue
                legalMoves = self.chess.getLegalMoves(p[0], p[1])
                if legalMoves[newRow][newCol] != 0:
                    if p[0] == oldRow:
                        needCol = self.coordsToAlgebraic(oldRow, oldCol)[0]
                    if p[1] == oldCol:
                        needRow = self.coordsToAlgebraic(oldRow, oldCol)[1]
            #print (f"Potrebujemo {needRow} {needCol}")
            return needRow + needCol
        except Exception as e:
            print(f"Napaka pri preverjanju dvoumnega poteza {e}")
            return None
    def addMoveNumber(self, move):
        return f"{self.turnNumber}. {move}"

    def generateMoveNotation(self, oldRow, oldCol, newRow, newCol):
        try:
            move = ""
            pieceNotation = {2: 'R', 3: 'N', 4: 'B', 5: 'Q', 6: 'K'}
            piece = self.chess.currBoard[oldRow][oldCol]
            capture = True
            if self.chess.currBoard[newRow][newCol] == 0:
                capture = False

            if abs(piece) == 6:
                if newRow == oldRow and newCol == oldCol + 2:
                    return self.addMoveNumber("O-O")
                elif newRow == oldRow and newCol == oldCol - 2:
                    return self.addMoveNumber("O-O-O")
            
            if abs(piece) == 1:
                if capture:
                    move += self.coordsToAlgebraic(oldRow, oldCol)[0] + 'x'
                move += self.coordsToAlgebraic(newRow, newCol)
            else:
                move += pieceNotation[abs(piece)]
                dodatek = self.isAmbiguousMove(oldRow, oldCol, newRow, newCol)
                if dodatek != None and dodatek != False:
                    move += dodatek
                
                if capture:
                    move += 'x'
                move += self.coordsToAlgebraic(newRow, newCol)
        

            return self.addMoveNumber(move)
        except Exception as e:
            print(f"Napaka pri generiranju notacije poteze: {e}")
            return None
        
    def isDuplicateId(self,unique_id):

        if (self.uniqueCodeC1 == unique_id and self.socketC1 is not None) or (self.uniqueCodeC2 == unique_id and self.socketC2 is not None):
            return True
        return False
    
    
    def saveToFile(self):
        try:
            directory = "IGRE"
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            file_path = os.path.join(directory, self.fileName)
            with open(file_path, 'w') as file:
                file.write(f"Game ID: {self.gameID}\n")
                file.write(f"Player 1: {self.uniqueCodeC1}\n")
                file.write(f"Player 2: {self.uniqueCodeC2}\n")
                file.write(f"Time white: {self.timeWhite}\n")
                file.write(f"Time black: {self.timeBlack}\n")
                file.write(f"Moves:\n")
                for move in self.moves:
                    file.write(f"{move}\n")
        except Exception as e:
            print(f"Napaka pri shranjevanju igre v datoteko: {e}")


    def surrender(self, unique_id):
        if self.uniqueCodeC1 == unique_id:
            return self.uniqueCodeC2
        return self.uniqueCodeC1
    
    def resetGame(self):
        self.chess = chessLogic.ChessBoard(0)

        self.whoIsWhite = random.randint(1, 2)
        self.chessBoard = self.chess.currBoard
        self.isWhiteTurn = True
        self.moves = []
        self.turnNumber = 0
        self.timeWhite = 600  # 10 minutes in seconds
        self.timeBlack = 600  # 10 minutes in seconds
        self.lastMoveTime = time.time()
    

    def checkTime(self):
        if self.moves == []:
            return False
        if self.isWhiteTurn:
            timeLeft = self.timeWhite - (time.time() - self.lastMoveTime)
        else:
            timeLeft = self.timeBlack - (time.time() - self.lastMoveTime)
        if timeLeft <= 0:
            if self.isWhiteTurn:
                return "W"
            else:
                return "B"
        return False
    
        

