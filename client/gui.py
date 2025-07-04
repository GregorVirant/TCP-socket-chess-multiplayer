import pygame
import colors
from button import *
import os
import sys

MENU = 0
GAME = 1
PICK_FIGURE = 2
GAME_END = 3
def getBackgroundTexturePath():
    try:
        with open("textures/texture_background.txt",'r') as file:
            line = file.readline().strip()
            if not line:
                print("File textures/texture_background.txt is empty.");
                return None
            else:
                return line;
    except Exception as e:
        print(f"Napaka pri branju texture_background: {e}.")
        return None
    
def getPiecesTextures():
    try:
        with open("textures/textures_pieces.txt",'r') as file:
            lines = file.readlines()
        if len(lines) < 2:
            print(f"File textures_pieces.txt does not have enough lines.")
            return None
        textures = []
        path = ""
        number = 0
        for i in range(len(lines)):
            if i%2 == 0:
                path = lines[i].strip()
            else:
                try:
                    number = int(lines[i].strip())
                    textures.append((path,number))
                except:
                    print("File textures_pieces.txt doesn not include numbers on correct lines.")
                    return None
        return textures;            
                
    except Exception as e:
        print(f"Napaka pri branju textures_pieces.txt: {e}.")
        return None

def getCurrentPiecesTextures():
    try:
        with open("textures/current_pieces_texture.txt",'r') as file:
            line = file.readline().strip()
            if not line:
                print("File textures/current_pieces_texture.txt is empty.");
                return None
            else:
                num = 0
                try:
                    num = int(line);
                except:
                    print("Content textures/current_pieces_texture.txt is not a file.");
                    return None
                return num
    except Exception as e:
        print(f"Napaka pri branju current_pieces_texture.txt: {e}.")
        return None
def writeCurrentPieceTexture(number):
    if not os.path.exists("textures/current_pieces_texture.txt"):
        return False
    try:
        with open("textures/current_pieces_texture.txt",'w') as file:
            file.write(str(number))
        return True
    except:
        return False

class Gui: 
    def __init__(self):
        pygame.init()
        self.state = MENU

        display_info = pygame.display.Info()
        display_width = display_info.current_w
        display_height = display_info.current_h

        self.borderWidth=100
        self.scale = (min(display_width,display_height)/(800+self.borderWidth*2))*0.8
        
        self.displayWidth=(800+2*self.borderWidth)*self.scale
        self.displayHeight=(800+2*self.borderWidth)*self.scale
        
        self.borderColor=(255,255,0)
        
        self.scaledScreen = pygame.display.set_mode([self.displayWidth,self.displayHeight])  

        #TITLE AND ICON
        pygame.display.set_caption("Chess")
        icon = pygame.image.load("textures/icon.png")
        pygame.display.set_icon(icon)

        b_texutre = getBackgroundTexturePath()
        if not b_texutre:
            sys.exit()
        try:
            self.background = pygame.image.load(b_texutre).convert()
        except:
            sys.exit()

        self.menu = pygame.Surface((800+2*self.borderWidth,800+2*self.borderWidth),pygame.SRCALPHA)

        self.board = pygame.Surface((800+2*self.borderWidth,800+2*self.borderWidth),pygame.SRCALPHA)
        self.square_size = 100
        self.mouseIsPressed = False

        self.textImages = [[],[],[],[]]
        self.textImagesCoordinates = [[],[],[],[]]
        self.textImagesPermanent = [[],[],[],[]]
        self.textImagesPermanentCoordinates = [[],[],[],[]]

        self.buttons = [[],[],[],[]]
        self.textFields = [[],[],[],[]]
        self.textFieldSelected=[None,None,None,None]

        self.colorsForLegalMoves=(colors.LIGHT_BLUE,colors.BLUE,colors.RED)

        self.textures = getPiecesTextures()
        if not self.textures:
            sys.exit()
        self.texture=getCurrentPiecesTextures()
        if self.texture == None or self.texture >= len(self.textures):
            sys.exit()

        self.mouseClicked = False

        self.eventQuit = False
        self.eventCharWritten = ""
        self.eventCharDeleted = False

        self.lastMoveStart = (-1,-1)
        self.lastMoveEnd = (-1,-1)

        self.whoseTurn = 0
        self.whoseMoveScale = 0.1 
    
    def getBorderWidth(self):
        return self.borderWidth

    def loadNextTexture(self):
        if self.texture >= len(self.textures):
            self.texture = 0
        self.loadTexture(self.textures[self.texture][0],self.textures[self.texture][1])
        if not writeCurrentPieceTexture(self.texture):
            print("Odpiranje current_piece_texture.txt neuspesno.")
            sys.exit()
        self.texture+=1
    
    def loadTexture(self,folder,texture_width):
        self.texturesWhite = []
        self.texturesBlack = []
        pieces=["Pawn","Rook","Knight","Bishop","Queen","King"] 
        try:
            for piece in pieces:
                self.texturesWhite.append(pygame.image.load(f"{folder}/white{piece}.png").convert_alpha())
                self.texturesBlack.append(pygame.image.load(f"{folder}/black{piece}.png").convert_alpha())
        except:
            print("Invalid piece textures")
            sys.exit()

        self.texture_width = texture_width
        self.texture_shift = (self.square_size-self.texture_width)/2 #zaradi razlike v velikosti polja in figur
        #h2/w2 = h1/w1  => h2=(h1*w2)/w1
        self.texture_hight = (self.texturesWhite[0].get_height() * self.texture_width)/self.texturesWhite[0].get_width()

        #SCALE TEXTURES
        for i in range(6): #6 number of different figures
            self.texturesWhite[i] = pygame.transform.scale(self.texturesWhite[i],(self.texture_width,self.texture_hight))
            self.texturesBlack[i] = pygame.transform.scale(self.texturesBlack[i],(self.texture_width,self.texture_hight)) 

    # def shouldQuit(self):
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             return True
    #     return False
    def loadEvents(self):
        self.eventCharDeleted=False
        self.eventCharWritten=""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.eventQuit = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.eventCharDeleted=True
                else:
                    self.eventCharWritten=event.unicode
    def shouldQuit(self):
        return self.eventQuit        
            
    def close(self):
        pygame.quit()

    def mouseClickedUpdate(self):
        position=pygame.mouse.get_pos()
        if (not self.mouseIsPressed) and pygame.mouse.get_pressed()[0]:
            self.mouseIsPressed=True
            #return True
            self.mouseClicked = True
            return
        if (not pygame.mouse.get_pressed()[0]):
            self.mouseIsPressed=False
        #return False
        self.mouseClicked=False
    
    def mouseClickedOnBoard(self):
        position=pygame.mouse.get_pos()
        if position[0]<(0+self.borderWidth)*self.scale or position[0]>=(800+self.borderWidth)*self.scale or position[1]<(0+self.borderWidth)*self.scale or position[1]>=(800+self.borderWidth)*self.scale:
            return False
        #return True ionstead of bottom
        return self.mouseClicked

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
    
    def addText(self,text,coordinates=(0,0),fontSize=50,color=colors.BLACK,font=None,bold=False,isPermanent=False):
        selectedFont = pygame.font.SysFont(font,fontSize,bold=bold)
        if isPermanent:
            self.textImagesPermanent[self.state].append(selectedFont.render(text,True,color))
            self.textImagesPermanentCoordinates[self.state].append(coordinates)        
            return
        self.textImages[self.state].append(selectedFont.render(text,True,color))
        self.textImagesCoordinates[self.state].append(coordinates)        

    def addButton(self,text,action,buttonCoordinates=(0,0),buttonSize=None,buttonColor = colors.WHITE,fontSize=50,textColor=colors.BLACK,font=None,borderRadius=0,hoverColor=colors.LIGHT_PURPLE,bold=False):#isPermanent
        selectedFont = pygame.font.SysFont(font,fontSize,bold=bold)
        textImage = selectedFont.render(text,True,textColor)

        if buttonSize:
            buttonRect = pygame.Rect(buttonCoordinates,buttonSize)
        else:
            buttonRect = pygame.Rect(buttonCoordinates,textImage.get_size())
        textImageRect = textImage.get_rect(center=buttonRect.center)
        b1=Button(textImage,textImageRect,buttonRect,action,buttonColor,borderRadius,hoverColor)
        self.buttons[self.state].append(b1) 
    def buttonsCalculateCliks(self):
        for button in self.buttons[self.state]:
            position=pygame.mouse.get_pos()
            posX=round(position[0]/self.scale)
            posY=round(position[1]/self.scale)
            if button.calculateClick(posX,posY,self.mouseClicked):
                return True
        return False    
    def addTextField(self,length,x,y,font=None,fontSize=40,bold=True,color=(255,255,255),borderColor=(0,0,0),selectedBorderColor=(255,0,0),hoveredBorderColor=(0,0,200),textColor=(0,0,0),borderWidth=4,borderRadius=5,onlyNumbers=False):
        tf = textField(length,x,y,font,fontSize,bold,color,borderColor,selectedBorderColor,hoveredBorderColor,textColor,borderWidth,borderRadius,onlyNumbers)
        self.textFields[self.state].append(tf)

    def readTextField(self,num):
        return self.textFields[self.state][num].read()

    def calculateSelectedTextField(self):
        for tf in self.textFields[self.state]:
            position=pygame.mouse.get_pos()
            posX=round(position[0]/self.scale)
            posY=round(position[1]/self.scale)
            tf1 = tf.selected(posX,posY,self.mouseClicked)
            if tf1:
                self.textFieldSelected[self.state]=tf1
                return True
        return False
    
    def hoverButtonsAndTextFields(self,posX,posY):
        
        for tf in self.textFields[self.state]:
            if tf.hover(posX,posY,self.textFieldSelected[self.state]):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                return
        for button in self.buttons[self.state]:
            if button.hover(posX,posY):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                return
        
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


    def buttonAndTextFieldCalculations(self):
        #ce en tekstfield selectan pogledamo ce klikjeno dolj drgace pisemo v njega
        position=pygame.mouse.get_pos()
        posX=round(position[0]/self.scale)
        posY=round(position[1]/self.scale)

        self.hoverButtonsAndTextFields(posX,posY)

        if self.textFieldSelected[self.state]:
            if self.mouseClicked and not self.textFieldSelected[self.state].selected(posX,posY,self.mouseClicked):
                #print("klikjen dolj")
                self.textFieldSelected[self.state]=None
            elif self.mouseClicked:
                #print("klikjen na sebe")
                self.textFieldSelected[self.state]=None
                return True
            else:
                if self.eventCharWritten:
                    self.textFieldSelected[self.state].write(self.eventCharWritten)
                if self.eventCharDeleted:
                    self.textFieldSelected[self.state].deleteLastChar()
                return True
        
        if self.calculateSelectedTextField():
            #print("selected a text field")
            return True
        
        if self.buttonsCalculateCliks():
            #print("selected a button")
            return True
        #print("selected nothing")
        return False

    def startGame(self):
        self.state = GAME
    def startMenu(self):
        self.state = MENU
    def draw(self,board=None,legalMoves=None):
        if self.state == MENU:
            self.drawMenu()
        elif self.state == PICK_FIGURE  or self.state == GAME_END:
            self.drawPickFigure()
        else:
            if board and legalMoves:
                self.drawGame(board,legalMoves)
    def drawPickFigure(self):
        self.board.fill(colors.PURPLE+(120,))
        for i, textImage in enumerate(self.textImages[self.state]):
            self.board.blit(textImage,self.textImagesCoordinates[self.state][i])
        self.textImages[self.state].clear()
        self.textImagesCoordinates[self.state].clear()

        for i, textImage in enumerate(self.textImagesPermanent[self.state]):
            self.board.blit(textImage,self.textImagesPermanentCoordinates[self.state][i])

        for button in self.buttons[self.state]:
            button.draw(self.board)

        for textField in self.textFields[self.state]:
            textField.draw(self.board)


        self.scaledScreen.blit(pygame.transform.scale(self.board, (self.displayWidth,self.displayHeight)),(0,0))
        pygame.display.flip()        

    def drawMenu(self):
        #self.menu.fill(colors.PURPLE)
        self.menu.blit(pygame.transform.scale(self.background,(800+2*self.borderWidth,800+2*self.borderWidth)),(0,0))
        for i, textImage in enumerate(self.textImages[self.state]):
            self.menu.blit(textImage,self.textImagesCoordinates[self.state][i])
        self.textImages[self.state].clear()
        self.textImagesCoordinates[self.state].clear()

        for i, textImage in enumerate(self.textImagesPermanent[self.state]):
            self.menu.blit(textImage,self.textImagesPermanentCoordinates[self.state][i])

        for button in self.buttons[self.state]:
            button.draw(self.menu)

        for textField in self.textFields[self.state]:
            textField.draw(self.menu)


        self.scaledScreen.blit(pygame.transform.scale(self.menu, (self.displayWidth,self.displayHeight)),(0,0))
        pygame.display.flip()


    def drawGame(self,board,colorMatrix):
        self.board.fill(colors.LIGHT_BLUE)
        if self.whoseTurn == 1:
            pygame.draw.rect(self.board,colors.LIGHT_YELLOW,(self.borderWidth*(1-self.whoseMoveScale),400+self.borderWidth,800+(self.borderWidth*self.whoseMoveScale*2),400+(self.borderWidth*self.whoseMoveScale)))
        if self.whoseTurn == -1:
            pygame.draw.rect(self.board,colors.CYAN,(self.borderWidth*(1-self.whoseMoveScale),self.borderWidth*(1-self.whoseMoveScale),800+(self.borderWidth*self.whoseMoveScale*2),400+(self.borderWidth*self.whoseMoveScale)))
        pygame.draw.rect(self.board,colors.LIGHT_PURPLE,(self.borderWidth,self.borderWidth,800,800))
        for i in range(8):
            for j in range(8):
                if (i % 2 == 1 and j % 2 == 0) or (j % 2 == 1 and i % 2 == 0):
                    pygame.draw.rect(self.board,colors.PURPLE,(self.square_size*j+self.borderWidth,self.square_size*i+self.borderWidth,self.square_size,self.square_size))
                if (i == self.lastMoveStart[0] and j == self.lastMoveStart[1]) or (i == self.lastMoveEnd[0] and j == self.lastMoveEnd[1]):
                    pygame.draw.rect(self.board, colors.DARK_YELLOW if (i % 2 == 1 and j % 2 == 0) or (j % 2 == 1 and i % 2 == 0) else colors.LIGHT_YELLOW, (self.square_size * j + self.borderWidth, self.square_size * i + self.borderWidth, self.square_size, self.square_size))
                if colorMatrix[i][j] != 0:
                    pygame.draw.rect(self.board,self.colorsForLegalMoves[colorMatrix[i][j]-1],(self.square_size*j+self.square_size*0.15+self.borderWidth,self.square_size*i+self.square_size*0.15+self.borderWidth,self.square_size-self.square_size*0.3,self.square_size-self.square_size*0.3))
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

        
        for i, textImage in enumerate(self.textImages[self.state]):
            self.board.blit(textImage,self.textImagesCoordinates[self.state][i])
        self.textImages[self.state].clear()
        self.textImagesCoordinates[self.state].clear()

        for i, textImage in enumerate(self.textImagesPermanent[self.state]):
            self.board.blit(textImage,self.textImagesPermanentCoordinates[self.state][i])

        for button in self.buttons[self.state]:
            button.draw(self.board)

        for textField in self.textFields[self.state]:
            textField.draw(self.board)

        #self.scaledScreen.blit(self.board,(0,0))
        self.scaledScreen.blit(pygame.transform.scale(self.board, (self.displayWidth,self.displayHeight)),(0,0))
        pygame.display.flip()

    def getTextSize(self, text, fontSize):
        font = pygame.font.Font(None, fontSize)
        text = font.render(text, True, colors.BLACK)
        return text.get_width()