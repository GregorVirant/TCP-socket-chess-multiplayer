import pygame
import colors

class Game: 
    def __init__(self,scale):
        pygame.init()
        self.scale = scale
        self.borderWidth=50
        self.displayWidth=(800+2*self.borderWidth)*scale
        self.displayHeight=(800+2*self.borderWidth)*scale
        #self.scaledScreen = pygame.display.set_mode([800*scale,800*scale])  
        
        self.borderColor=(255,255,0)
        self.scaledScreen = pygame.display.set_mode([self.displayWidth,self.displayHeight])  
        self.board = pygame.Surface((800+2*self.borderWidth,800+2*self.borderWidth))
        #self.boardWithBorder = pygame.Surface((800+self.borderWidth*2,800+self.borderWidth*2))
        self.square_size = 100
        self.mouseIsPressed = False
        
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
    def mouseClickedOnBoard(self):
        position=pygame.mouse.get_pos()
        if (not self.mouseIsPressed) and pygame.mouse.get_pressed()[0]:
            if position[0]<(0+self.borderWidth)*self.scale or position[0]>=(800+self.borderWidth)*self.scale or position[1]<(0+self.borderWidth)*self.scale or position[1]>=(800+self.borderWidth)*self.scale:
                return False
            self.mouseIsPressed=True
            return True
        if (not pygame.mouse.get_pressed()[0]):
            self.mouseIsPressed=False
        return False
        #return pygame.mouse.get_pressed()[0]==1
        #return True

    def mouseGetBoardPosition(self):
        position=pygame.mouse.get_pos()
        #print(position)
        posX=(round(position[0]/self.scale)-self.borderWidth)//self.square_size
        posY=(round(position[1]/self.scale)-self.borderWidth)//self.square_size
        #posX=(position[0]-self.borderWidth)//self.square_size
        #posY=(position[1]-self.borderWidth)//self.square_size
        if posX>7:
            posX=7
        if posY>7:
            posY=7
        return (posX,posY)
    

    # def mousePosition(self):
    #     return pygame.mouse.get_pos()
    def draw(self,board,colorMatrix,colorToMove):
        self.board.fill(colors.LIGHT_BLUE)
        pygame.draw.rect(self.board,colors.LIGHT_PURPLE,(self.borderWidth,self.borderWidth,800,800))

        for i in range(8):
            for j in range(8):
                if (i % 2 == 1 and j % 2 == 0) or (j % 2 == 1 and i % 2 == 0):
                    pygame.draw.rect(self.board,colors.PURPLE,(self.square_size*j+self.borderWidth,self.square_size*i+self.borderWidth,self.square_size,self.square_size))
                if colorMatrix[j][i] == 1:
                    pygame.draw.rect(self.board,colors.BLUE,(self.square_size*j+self.square_size*0.15+self.borderWidth,self.square_size*i+self.square_size*0.15+self.borderWidth,self.square_size-self.square_size*0.3,self.square_size-self.square_size*0.3))
                if(board[i][j]==0):
                    continue
                #if(board[i][j]==1):self.board.blit(self.texturesWhite[0],(45*j,45*i))
                if(board[i][j]>0):
                    #if colorToMove == 1:
                    #   pygame.draw.rect(self.board,colors.BLUE,(45*j+8,45*i+8,45-16,45-16))
                    self.board.blit(self.texturesWhite[board[i][j]-1],(self.square_size*j+self.texture_shift+self.borderWidth,self.square_size*i-self.texture_hight+self.texture_width+self.texture_shift+self.borderWidth))
                else:
                    #print((board[i][j])*-1-1)
                    self.board.blit(self.texturesBlack[(board[i][j])*-1-1],(self.square_size*j+self.texture_shift+self.borderWidth,self.square_size*i-self.texture_hight+self.texture_width+self.texture_shift+self.borderWidth))

        #self.scaledScreen.blit(self.board,(0,0))
        self.scaledScreen.blit(pygame.transform.scale(self.board, (self.displayWidth,self.displayHeight)),(0,0))
        pygame.display.flip()