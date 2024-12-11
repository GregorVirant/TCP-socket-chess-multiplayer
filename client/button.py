import pygame
class Button():
    def __init__(self,textImage,textImagePos,rect,action,buttonColor,borderRadius,hoverColor):
        self.textImage=textImage
        self.textImagePos=textImagePos
        self.rect=rect
        self.action=action
        self.defaultColor=buttonColor
        self.buttonColor=buttonColor
        self.borderRadius=borderRadius
        self.hoverColor=hoverColor
    def draw(self,surface): 
        #Draws the button rectangle and the text on top of it
        pygame.draw.rect(surface,self.buttonColor,self.rect,border_radius=self.borderRadius)
        surface.blit(self.textImage,self.textImagePos)  
    def calculateClick(self,posX,posY,isPressed):
        #colors the button if is hover over with a mouse,and starts the action if the button is clicked
        if self.rect.collidepoint((posX,posY)):
            #self.buttonColor=self.hoverColor
            if isPressed:
                self.action()
                return True
        #else:
            #self.buttonColor=self.defaultColor
        return False
    def hover(self,posX,posY):
        if self.rect.collidepoint((posX,posY)):
            self.buttonColor=self.hoverColor
            return True
        else:
            self.buttonColor=self.defaultColor
            return False
    
class textField():
    def __init__(self,length,x,y,font,fontSize,bold,color,borderColor,selectedBorderColor,hoveredBorderColor,textColor,borderWidth,borderRadius,onlyNumbers):
        self.text=""
        self.lenght=length
        self.color=color
        self.defualtBorderColor=borderColor
        self.borderColor=self.defualtBorderColor
        self.selectedBorderColor=selectedBorderColor
        self.textColor=textColor
        self.borderRadius=borderRadius
        self.borderWidth=borderWidth
        self.hoveredBorderColor=hoveredBorderColor
        self.onlyNumbers=onlyNumbers

        self.isSelected = False

        self.font = pygame.font.SysFont(None, 30) #,bold=bold
        for i in range(length+1):
            self.text+="A"
        width,height=self.font.size(self.text)
        self.rect=pygame.Rect(x,y,width,height)
        self.text=" "

    def draw(self, surface):
        textImage = self.font.render(self.text,True,self.textColor)
        borderRect = pygame.Rect(self.rect.left-self.borderWidth,self.rect.top-self.borderWidth,self.rect.width+self.borderWidth*2,self.rect.height+self.borderWidth*2)
        pygame.draw.rect(surface,self.borderColor,borderRect,border_radius=self.borderRadius)
        pygame.draw.rect(surface,self.color,self.rect,border_radius=self.borderRadius)
        surface.blit(textImage,self.rect)  
    def write(self,char):
        if self.onlyNumbers and not char.isdigit():
            return
        if len(self.text)-1+1>self.lenght:
            return #False
        self.text+=char.upper()
    def deleteLastChar(self):
        if len(self.text)<=1:
            return
        self.text=self.text[0:-1]
    def clear(self):
        self.text=" "
    def read(self):
        return self.text[1:]
    def selected(self,posX,posY,isPressed):
        if self.rect.collidepoint((posX,posY)):
            if isPressed:
                self.isSelected=True
                self.borderColor=self.selectedBorderColor
                return self
        return None
    def hover(self,posX,posY,textField):
        if self == textField:
            return False
        if self.rect.collidepoint((posX,posY)):

            self.borderColor=self.hoveredBorderColor
            return True
        else:
            self.borderColor=self.defualtBorderColor
        return False