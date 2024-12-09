class Game:
    #GAME ID JE SAMO POZICIJA KI JE V ARRAYI
    def __init__(self,socketC1,uniqueCodeC1):
        self.socketC1=socketC1
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

    def isOneSpaceEmpty(self): #ce se ni not gledamo ce slucajno se igra fraj
        #return !uniqueCodeC2 #CE JE None JE SE PRAZNO
        pass