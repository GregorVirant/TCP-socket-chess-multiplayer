#import draw
from game import *
from logic import *




run = True
game=Game(1.3)  #class for displaying the game and taking user input   (game scale)
game.loadNextTexture() #loads figure textures (folder for textures, figures scale)

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

isWhiteToMove=[True]

def create():
        print(f"#CREATE|{game.textFields[0].read()[1:]}|")
        game.textFields[0].clear()
def join():
        print(f"#JOIN|{game.textFields[0].read()[1:]}|")
        game.textFields[0].clear()

game.addButton("Change texture",game.loadNextTexture,(630,5),(220,30),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=24,bold=True,font="arial")

game.addTextField(5,54,865)
#game.addTextField(5,300,865)
game.addButton("Create",create,(150,861),(70,28),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=18,bold=True,font="arial")
game.addButton("Join",join,(230,861),(70,28),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=18,bold=True,font="arial")      

chessBoard = ChessBoard(BoardType.STANDARD)
while run:
        #can add fps limit
        game.loadEvents()
        run=not game.shouldQuit()
        #Should run on every cycle
        game.mouseClickedUpdate()       

        clicked = game.buttonAndTextFieldCalculations()
        
        if not clicked and game.mouseClickedOnBoard(): 
                position=game.mouseGetBoardPosition() #x,y (column,row)
                row=position[1]
                column=position[0]

                
                if legalMoves[row][column]==1: #when user click on the already selected square

                        clearLegalMoves(legalMoves)

                elif legalMoves[row][column] == 0: #when user click on a non selected square

                        legalMoves = chessBoard.getLegalMoves(row, column)
                else: #user already selected a piece, now he wants to move it

                        pieceRow=0
                        pieceColumn=0
                        for i in range(8):
                                for j in range(8):
                                        if legalMoves[i][j]==1:
                                                pieceRow=i
                                                pieceColumn=j
                                                isWhiteToMove[0]=not isWhiteToMove[0]
                        chessBoard.makeMove((pieceRow, pieceColumn),(row, column))
                        move(pieceRow,pieceColumn,row,column,board)
                        legalMoves = chessBoard._getEmptyBoard()
                

        game.addText("Beli na potezi." if chessBoard.isWhiteToMove else "Črni na potezi",(50,0),fontSize=30,font="Comic Sans MS", color=colors.BLACK,bold=True)


        #print(legalMoves)
        game.draw(chessBoard.getBoard(),legalMoves)
game.close()