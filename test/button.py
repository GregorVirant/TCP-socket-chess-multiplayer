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
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            self.buttonColor=self.hoverColor
            if isPressed:
                self.action()
                return True
        else:
            self.buttonColor=self.defaultColor
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        return False