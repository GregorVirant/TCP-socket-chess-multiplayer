import chessLogic
import random
import time
class Game:
    #GAME ID JE SAMO POZICIJA KI JE V ARRAYI
    def __init__(self, gameID,socketC1,uniqueCodeC1):
        self.gameID = gameID
        self.socketC1 = socketC1
        self.uniqueCodeC1 = uniqueCodeC1
        self.socketC2 = None
        self.uniqueCodeC2 = None

        self.chess = chessLogic.ChessBoard(0)

        self.whoIsWhite = random.randint(1, 2)
        self.chessBoard = self.chess.currBoard
        self.isWhiteTurn = True

        self.turnNumber = 0

        self.timeWhite = 600  # 10 minutes in seconds
        self.timeBlack = 600  # 10 minutes in seconds
        self.lastMoveTime = time.time()

    def isPlayerTurn(self, uniqueId):
        if self.whoIsWhite == 1:
            return (uniqueId == self.uniqueCodeC1 and self.isWhiteTurn) or (uniqueId == self.uniqueCodeC2 and not self.isWhiteTurn)
        else:
            return (uniqueId == self.uniqueCodeC1 and not self.isWhiteTurn) or (uniqueId == self.uniqueCodeC2 and self.isWhiteTurn)
    
    def _updateBoard(self):
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
        self.chess.makeMove(odlSquare, newSquare)
        self._updateBoard()
        self._updateTime()
        self.isWhiteTurn = not self.isWhiteTurn
        self.turnNumber += 1
        
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
        print(f"Zahteva za izhod iz igre {self.gameID} od igralca {unique_id}")
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

