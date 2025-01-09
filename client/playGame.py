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

gui=Gui(1) #class for displaying the game and taking user input   (game scale)
run = True

def back():
    global run
    sendingAndReciving.timerStarted = False
    run = False

def surre():
    send_message("#SURRENDER")

def enumerateBoard():
    print("TODO")


gui.state = GAME
gui.addButton("Back",back,(630+50,860+100),(220,30),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=18,bold=True,font="arial")
gui.addButton("Surrender",surre,(400+50,860+100),(220,30),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=18,bold=True,font="arial")
gui.addButton("Oštevilči",enumerateBoard,(400+50,5),(220,30),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=24,bold=True,font="arial")
gui.addButton("Change texture",gui.loadNextTexture,(630+50,5),(220,30),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=24,bold=True,font="arial")
gui.state = MENU

def play(gui):
    global run
    #send_message("#M", client, f"{current_game_code}:{message}")
    #position=game.mouseGetBoardPosition()
    selectedPosition = None
    
    gui.state = GAME
    gui.startGame()
    
    while run:
        if sendingAndReciving.connectionError:
            print ("Connection error")
            run = False
            
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
            
            if selectedPosition is None and board[row][column] != 0 or (legalMoves[row][column] != 2 and legalMoves[row][column] != 3):
                selectedPosition = (row, column)
                send_message("#GETLEGALMOVES", message=f"{selectedPosition[0]}:{selectedPosition[1]}")
            elif selectedPosition is not None and (legalMoves[row][column] == 2 or legalMoves[row][column] == 3):
                if selectedPosition != (row, column):
                    print("Sending move")
                    send_message("#MOVE", message=f"{selectedPosition[0]}:{selectedPosition[1]}:{row}:{column}")
                    selectedPosition = None
                    for i in range(8):
                        for j in range(8):
                            legalMoves[i][j] = 0
            else:
                selectedPosition = None

        gui.addText("Beli na potezi." if sendingAndReciving.isWhiteTurn else "Črni na potezi",(50+50,0),fontSize=30,font="Comic Sans MS", color=colors.BLACK,bold=True)
        gui.addText(sendingAndReciving.Time,(50+50,855+100),fontSize=30,font="Comic Sans MS", color=colors.BLACK,bold=True)
        #gui.addText("Beli na potezi.",(50,0),fontSize=30,font="Comic Sans MS", color=colors.BLACK,bold=True)

        gui.lastMoveStart = sendingAndReciving.lastMoveStart
        gui.lastMoveEnd = sendingAndReciving.lastMoveEnd
        gui.wasLastMoveMine = sendingAndReciving.wasLastMoveMine
        gui.draw(board,legalMoves)
        


    gui.startMenu()
    gui.state = MENU
    run = True
    closeConnection()