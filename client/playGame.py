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

gui=Gui() #class for displaying the game and taking user input
run = True

def back():
    global run
    sendingAndReciving.timerStarted = False
    run = False

def surre():
    send_message("#SURRENDER")

SHOW_ENUMERATION = False # variable that tells if the enumeration on board should be shown

is_enumerated = True

def enumerateBoard():
    global is_enumerated
    is_enumerated = not is_enumerated

def caculateBoardValue(board):
    values = {0:0,1:1, 2:5, 3:3, 4:3, 5:9, 6:9}
    sum = 0
    for row in board:
        for piece in row:
            if piece > 0:
                sum += values[piece]
            else:
                sum -= values[abs(piece)]
    if sum > 0:
        return f"+{sum}"
    return f"{sum}"

end_back_button = False
def setEndBackButton():
    global end_back_button
    end_back_button = True

gui.state = GAME
gui.addButton("Back",back,(630+50,860+100),(220,30),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=18,bold=True,font="arial")
gui.addButton("Surrender",surre,(400+50,860+100),(220,30),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=18,bold=True,font="arial")
gui.addButton("Enumerate",enumerateBoard,(400+50,5),(220,30),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=24,bold=True,font="arial")
gui.addButton("Change texture",gui.loadNextTexture,(630+50,5),(220,30),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=24,bold=True,font="arial")


gui.state = PICK_FIGURE

def pickPiece(p1): sendingAndReciving.promotion_pick = p1
gui.addButton("Rook",lambda: pickPiece(2),(600,300),(200,50),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=18,bold=True,font="arial")
gui.addButton("Knight",lambda: pickPiece(3),(600,400),(200,50),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=18,bold=True,font="arial")
gui.addButton("Bishop",lambda: pickPiece(4),(600,500),(200,50),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=18,bold=True,font="arial")
gui.addButton("Queen",lambda: pickPiece(5),(600,600),(200,50),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=18,bold=True,font="arial")

gui.state = GAME_END

gui.addButton("Main menu",setEndBackButton,(400,470),(200,50),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.PURPLE,borderRadius=5,fontSize=18,bold=True,font="arial")

gui.state = MENU

def play(gui):
    global run,end_back_button
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

        if sendingAndReciving.game_ended:
            #print(gui.state)
            #print("GAME END:  ",sendingAndReciving.game_end_message)
            gui.state = GAME_END
            textWidth = gui.getTextSize(sendingAndReciving.game_end_message,80)
            gui.addText(sendingAndReciving.game_end_message,coordinates=(1000 /2-(textWidth/2),390),fontSize=80,color=colors.BLACK,bold=True)
            gui.draw()

            while not end_back_button:
                gui.loadEvents()
                if gui.shouldQuit():
                    run = False
                    break
                gui.mouseClickedUpdate()     
                clicked = gui.buttonAndTextFieldCalculations()  
                #gui.draw()
            sendingAndReciving.game_ended = False
            end_back_button = False
            run = False
        if not sendingAndReciving.gameStarted:
            #print("Waiting for game to start")
            gui.addText("WAITING FOR",coordinates=((1000-gui.getTextSize("WAITING FOR", 115))/2,300),fontSize=115,color=colors.BLACK,bold=True)
            gui.addText("OPPONENT",coordinates=((1000 - gui.getTextSize("OPPONENT", 115))/2,390),fontSize=115,color=colors.BLACK,bold=True)
            if sendingAndReciving.current_game_code:
                gui.addText(f"Code:  {sendingAndReciving.current_game_code.upper()}",coordinates=((1000 - gui.getTextSize(f"Code:  {sendingAndReciving.current_game_code.upper()}", 110))/2,480),fontSize=110,color=colors.BLACK,bold=True)
            gui.draw(board,legalMoves)
            continue

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
                    #print("CHOSEN")
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
                    #print("Sending move")
                    send_message("#MOVE", message=f"{selectedPosition[0]}:{selectedPosition[1]}:{row}:{column}")
                    selectedPosition = None
                    for i in range(8):
                        for j in range(8):
                            legalMoves[i][j] = 0
            else:
                selectedPosition = None
        
        if is_enumerated:
            board_orientation_white = sendingAndReciving.amIWhite
            turn = 1 - 2 * (not board_orientation_white)

            for i in range(8):
                gui.addText(text=str(i+1), coordinates=(60, ((900 - turn*(i+1) * 100) % 900) +30))
                gui.addText(text=chr(i + ord('a')), coordinates=((940 + 100 * turn * (i+1)) % 900, 915))
       
            

        gui.addText("White to move." if sendingAndReciving.isWhiteTurn else "Black to move",(50+50,0),fontSize=30,font="Comic Sans MS", color=colors.BLACK,bold=True)
        gui.addText(sendingAndReciving.Time,(50+50,855+100),fontSize=30,font="Comic Sans MS", color=colors.BLACK,bold=True)
        gui.addText(text=f"material balance: {caculateBoardValue(board)}", coordinates=(570, 50))
        #gui.addText("Beli na potezi.",(50,0),fontSize=30,font="Comic Sans MS", color=colors.BLACK,bold=True)

        gui.lastMoveStart = sendingAndReciving.lastMoveStart
        gui.lastMoveEnd = sendingAndReciving.lastMoveEnd

        whoseTurn = 0
        if (sendingAndReciving.amIWhite and sendingAndReciving.isWhiteTurn) or ((not sendingAndReciving.amIWhite) and (not sendingAndReciving.isWhiteTurn)):
            whoseTurn = 1
        else:
            whoseTurn = -1
        gui.whoseTurn = whoseTurn
        gui.draw(board,legalMoves)
        

    for i in range(8):
        for j in range(8):
            legalMoves[i][j]=0
    gui.state = MENU
    sendingAndReciving.gameStarted = False
    gui.lastMoveStart = (-1,-1)
    gui.lastMoveEnd = (-1,-1)
    sendingAndReciving.lastMoveStart = (-1,-1)
    sendingAndReciving.lastMoveEnd = (-1,-1)
    gui.whoseTurn = 0
    run = True
    closeConnection()