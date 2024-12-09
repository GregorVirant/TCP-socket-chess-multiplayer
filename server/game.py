class Game:
    #GAME ID JE SAMO POZICIJA KI JE V ARRAYI
    def __init__(self, gameID,socketC1,uniqueCodeC1):
        self.gameID = gameID
        self.socketC1 = socketC1
        self.uniqueCodeC1 = uniqueCodeC1
        self.socketC2 = None
        self.uniqueCodeC2 = None  

        self.chessBoard = None   

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

