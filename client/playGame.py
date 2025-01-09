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

SHOW_ENUMERATION = False # variable that tells if the enumeration on board should be shown

is_enumerated = False

def enumerateBoard():
    global is_enumerated
    is_enumerated = not is_enumerated

gui.state = GAME
gui.addButton("Back",back,(630+50,860+100),(220,30),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=18,bold=True,font="arial")
gui.addButton("Surrender",surre,(400+50,860+100),(220,30),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=18,bold=True,font="arial")
gui.addButton("Oštevilči",enumerateBoard,(400+50,5),(220,30),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=24,bold=True,font="arial")
gui.addButton("Change texture",gui.loadNextTexture,(630+50,5),(220,30),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=24,bold=True,font="arial")


gui.state = PICK_FIGURE

def pickPiece(p1): sendingAndReciving.promotion_pick = p1
gui.addButton("Rook",lambda: pickPiece(2),(600,300),(200,50),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=18,bold=True,font="arial")
gui.addButton("Knight",lambda: pickPiece(3),(600,400),(200,50),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=18,bold=True,font="arial")
gui.addButton("Bishop",lambda: pickPiece(4),(600,500),(200,50),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=18,bold=True,font="arial")
gui.addButton("Queen",lambda: pickPiece(5),(600,600),(200,50),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=18,bold=True,font="arial")


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

        if not sendingAndReciving.gameStarted:
            #print("Waiting for game to start")
            gui.addText("WAITING FOR",coordinates=(175,300),fontSize=115,color=colors.BLACK,bold=True)
            gui.addText("OPPONENT",coordinates=(175,390),fontSize=115,color=colors.BLACK,bold=True)
            gui.addText(f"Code:  {sendingAndReciving.current_game_code.upper()}",coordinates=(175,480),fontSize=110,color=colors.BLACK,bold=True)
            gui.draw(board,legalMoves)
            continue;

        if sendingAndReciving.promoting:
            #piece = pickFigure(gui)
            #sendingAndReciving.send_message("#MOVE",message=f"{sendingAndReciving.promotion_message}:{piece}")
            gui.state = PICK_FIGURE
            sendingAndReciving.promoting = False
            gui.draw()
            while (True):
                gui.loadEvents()
                if gui.shouldQuit():
                    run = False
                    break
                gui.mouseClickedUpdate()     
                clicked = gui.buttonAndTextFieldCalculations()  
                if sendingAndReciving.promotion_pick != 0:
                    print("CHOSEN")
                    sendingAndReciving.send_message("#MOVE",message=f"{sendingAndReciving.promotion_message}:{sendingAndReciving.promotion_pick}")

                    sendingAndReciving.promotion_pick = 0
                    gui.state = GAME
                    gui.draw()
                    break

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
        
        if is_enumerated:
            board_orientation_white = sendingAndReciving.isWhiteTurn
            turn = 1 - 2 * (not board_orientation_white)

            for i in range(8):
                gui.addText(text=str(i+1), coordinates=(70, ((900 - turn*(i+1) * 100) % 900) +30))
                gui.addText(text=chr(i + ord('a')), coordinates=((940 + 100 * turn * (i+1)) % 900, 900))
       
            

        gui.addText("Beli na potezi." if sendingAndReciving.isWhiteTurn else "Črni na potezi",(50+50,0),fontSize=30,font="Comic Sans MS", color=colors.BLACK,bold=True)
        gui.addText(sendingAndReciving.Time,(50+50,855+100),fontSize=30,font="Comic Sans MS", color=colors.BLACK,bold=True)
        #gui.addText("Beli na potezi.",(50,0),fontSize=30,font="Comic Sans MS", color=colors.BLACK,bold=True)

        gui.lastMoveStart = sendingAndReciving.lastMoveStart
        gui.lastMoveEnd = sendingAndReciving.lastMoveEnd
        gui.draw(board,legalMoves)
        


    gui.startMenu()
    gui.state = MENU
    run = True
    closeConnection()