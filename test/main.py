#import draw
from game import *
from logic import *



run = True
game=Game(1.3)  #class for displaying the game and taking user input   (game scale)
game.loadTexture("pieces1",85) #loads figure textures (folder for textures, figures scale)

board=[[-2,-3,-4,-5,-6,-4,-3,-2],
        [-1,-1,-1,-1,-1,-1,-1,-1],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [1,1,1,1,1,1,1,1],
        [2,3,4,5,6,4,3,2]]

#current 1  legal moves 2   legal take 3
legalMoves=[[0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0]]

while run:
        #can add fps limit
        run=not game.shouldQuit()

        if game.mouseClickedOnBoard(): 
                position=game.mouseGetBoardPosition() #x,y (column,row)
                row=position[1]
                column=position[0]
                
                if legalMoves[row][column]==1: #when user click on the already selected square
                        clearLegalMoves(legalMoves)

                elif legalMoves[row][column]==0: #when user click on a non selected square
                        clearLegalMoves(legalMoves)
                        calculateLegalMoves(row,column,board,legalMoves)

                else: #user already selected a piece, now he wants to move it
                        pieceRow=0
                        pieceColumn=0
                        for i in range(8):
                                for j in range(8):
                                        if legalMoves[i][j]==1:
                                                pieceRow=i
                                                pieceColumn=j
                        move(pieceRow,pieceColumn,row,column,board)
                        clearLegalMoves(legalMoves)
                

                        


                        
                                        





        game.draw(board,legalMoves,1)
game.close()