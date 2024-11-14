import pygame
import colors

class Game: 
    def __init__(self,scale):
        pygame.init()
        self.scale = scale
        self.scaledScreen = pygame.display.set_mode([800*scale,800*scale])  
        self.screen = pygame.Surface((800,800))
        self.square_size = 100
        
    def loadTexture(self,folder = "pieces",texture_width=100):
        self.texturesWhite = []
        self.texturesBlack = []
        pieces=["Pawn","Rook","Knight","Bishop","Queen","King"]
        for piece in pieces:
            self.texturesWhite.append(pygame.image.load(f"textures/{folder}/white{piece}.png").convert_alpha())
            self.texturesBlack.append(pygame.image.load(f"textures/{folder}/black{piece}.png").convert_alpha())
            # self.texturesWhite.append(pygame.transform.scale(pygame.image.load(f"textures/pieces/white{piece}.png").convert_alpha(),(100,100)))
            # self.texturesBlack.append(pygame.transform.scale(pygame.image.load(f"textures/pieces/black{piece}.png").convert_alpha(),(100,100)))

        self.texture_width = texture_width
        self.texture_shift = (self.square_size-self.texture_width)/2 #zaradi razlike v velikosti polja in figur
        #h2/w2 = h1/w1  => h2=(h1*w2)/w1
        self.texture_hight = (self.texturesWhite[0].get_height() * self.texture_width)/self.texturesWhite[0].get_width()

        #SCALE TEXTURES
        for i in range(6): #6 number of different figures
            self.texturesWhite[i] = pygame.transform.scale(self.texturesWhite[i],(self.texture_width,self.texture_hight))
            self.texturesBlack[i] = pygame.transform.scale(self.texturesBlack[i],(self.texture_width,self.texture_hight))
        
    def shouldQuit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
        return False
    def close(self):
        pygame.quit()
    def mouseIsClicked(self):
        return pygame.mouse.get_pressed()[0]==1
        #return True
    def mouseGetBoardPosition(self):
        position=pygame.mouse.get_pos()
        return (position[0]//self.square_size,position[1]//self.square_size)
    # def mousePosition(self):
    #     return pygame.mouse.get_pos()
    def draw(self,board,colorMatrix,colorToMove):
        self.screen.fill(colors.LIGHT_PURPLE)

        for i in range(8):
            for j in range(8):
                if (i % 2 == 1 and j % 2 == 0) or (j % 2 == 1 and i % 2 == 0):
                    pygame.draw.rect(self.screen,colors.PURPLE,(self.square_size*j,self.square_size*i,self.square_size,self.square_size))
                if colorMatrix[j][i] == 1:
                    pygame.draw.rect(self.screen,colors.BLUE,(self.square_size*j+self.square_size*0.15,self.square_size*i+self.square_size*0.15,self.square_size-self.square_size*0.3,self.square_size-self.square_size*0.3))
                if(board[i][j]==0):
                    continue
                #if(board[i][j]==1):self.screen.blit(self.texturesWhite[0],(45*j,45*i))
                if(board[i][j]>0):
                    #if colorToMove == 1:
                    #   pygame.draw.rect(self.screen,colors.BLUE,(45*j+8,45*i+8,45-16,45-16))
                    self.screen.blit(self.texturesWhite[board[i][j]-1],(self.square_size*j+self.texture_shift,self.square_size*i-self.texture_hight+self.texture_width+self.texture_shift))
                else:
                    #print((board[i][j])*-1-1)
                    self.screen.blit(self.texturesBlack[(board[i][j])*-1-1],(self.square_size*j+self.texture_shift,self.square_size*i-self.texture_hight+self.texture_width+self.texture_shift))

        #self.screen.blit(self.texturesWhite[4],(20,20))
        self.scaledScreen.blit(pygame.transform.scale(self.screen,(800*self.scale,800*self.scale)),(0,0))
        pygame.display.flip()