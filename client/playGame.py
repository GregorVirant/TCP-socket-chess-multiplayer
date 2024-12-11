from gui import *
import sendingAndReciving
from sendingAndReciving import closeConnection,startSocket,setGameCode, send_message

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

gui=Gui(1.3) #class for displaying the game and taking user input   (game scale)
run = True

def back():
    global run
    run = False

gui.state = GAME
gui.addButton("Back",back,(630,860),(220,30),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=18,bold=True,font="arial")
gui.addButton("Change texture",gui.loadNextTexture,(630,5),(220,30),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=24,bold=True,font="arial")
gui.state = MENU

def play(gui):
    global run
    #send_message("#M", client, f"{current_game_code}:{message}")
    #position=game.mouseGetBoardPosition()
    gui.state = GAME
    gui.startGame()
    
    while run:
        gui.loadEvents()
        if gui.shouldQuit():
            #tu se tak event seta tak da bo pol tut iz main quital
            #gui.eventQuit=False
            #return
            run = False
        gui.mouseClickedUpdate()     
        clicked = gui.buttonAndTextFieldCalculations()  
        if not clicked and gui.mouseClickedOnBoard(): 
            column, row = gui.mouseGetBoardPosition()
            send_message("#GETLEGALMOVES", message=f"{row}:{column}")

            #game.addText("Beli na potezi." if chessBoard.isWhiteToMove else "Črni na potezi",(50,0),fontSize=30,font="Comic Sans MS", color=colors.BLACK,bold=True)
        gui.addText("Beli na potezi.",(50,0),fontSize=30,font="Comic Sans MS", color=colors.BLACK,bold=True)
        gui.draw(board,legalMoves)
    


    gui.startMenu()
    gui.state = MENU
    run = True
    closeConnection()