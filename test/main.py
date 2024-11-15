#import draw
from draw import *



run = True
game=Game(1)
#game.loadTexture()
game.loadTexture("pieces1",80)

board=[[-2,-3,-4,-5,-6,-4,-3,-2],
               [-1,-1,-1,-1,-1,-1,-1,-1],
               [0,0,0,0,0,0,0,0],
               [0,0,0,0,0,0,0,0],
               [0,0,0,0,0,0,0,0],
               [0,0,0,0,0,0,0,0],
               [1,1,1,1,1,1,1,1],
               [2,3,4,5,6,4,3,2]]
colorMatrix=[[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]]

while run:
        run=not game.shouldQuit()

        if game.mouseClickedOnBoard():
                position=game.mouseGetBoardPosition()
                colorMatrix[position[0]][position[1]]=1

        # print(game.isMouseClicked())

        game.draw(board,colorMatrix,1)
game.close()