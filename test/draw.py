import pygame

class Game: 
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode([360,360])  
        
    def loadTexture(self):
        self.texturesWhite = []
        self.texturesBlack = []
        pieces=["Pawn","Rook","Knight","Bishop","Queen","King"]
        for piece in pieces:
            self.texturesWhite.append(pygame.image.load(f"textures/pieces/white{piece}.png").convert_alpha())
            self.texturesBlack.append(pygame.image.load(f"textures/pieces/black{piece}.png").convert_alpha())
        
    def shouldQuit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
        return False
    def close(self):
        pygame.quit()
    def draw(self,board):
        self.screen.fill((235,235,255))

        for i in range(8):
            for j in range(8):
                if (i % 2 == 1 and j % 2 == 0) or (j % 2 == 1 and i % 2 == 0):
                    pygame.draw.rect(self.screen,(200,200,255),(45*j,45*i,45,45))
                if(board[i][j]==0):
                    continue
                #if(board[i][j]==1):self.screen.blit(self.texturesWhite[0],(45*j,45*i))
                if(board[i][j]>0):
                    self.screen.blit(self.texturesWhite[board[i][j]-1],(45*j,45*i))
                else:
                    #print((board[i][j])*-1-1)
                    self.screen.blit(self.texturesBlack[(board[i][j])*-1-1],(45*j,45*i))

        #self.screen.blit(self.texturesWhite[4],(20,20))
        pygame.display.flip()