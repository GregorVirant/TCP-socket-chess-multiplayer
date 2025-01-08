#MAIN ODJEMALEC
from gui import *
import playGame
from playGame import gui
from time import sleep
from threading import Thread

run = True
gui.loadNextTexture() #loads figure textures (folder for textures, figures scale)

uniqueIDRequiered = False
gameCodeRequiered = False
errorText = ""
startGameFlag = False  # Zastavica za začetek igre

def waitForGameCodeResponse():
    global errorText, startGameFlag  # Declare errorText and startGameFlag as global
    errorText = "Waiting for server response"
    for i in range(31):
        if i == 30:
            errorText = "No response from server"
            return
        elif playGame.sendingAndReciving.validGameCode == "N/A":
            pass
        elif playGame.sendingAndReciving.validGameCode == "True":
            startGameFlag = True  # Nastavi zastavico za začetek igre
            break
        elif playGame.sendingAndReciving.validGameCode == "False":
            errorText = "Invalid game code"
            return
        else:
            return
        sleep(0.1)

def getTextSize(text, fontSize):
    font = pygame.font.Font(None, fontSize)
    text = font.render(text, True, colors.BLACK)
    return text.get_width()

def createGame():
    global uniqueIDRequiered, gameCodeRequiered, errorText
    errorText = ""
    if not playGame.startSocket(playGame.board, playGame.legalMoves):
        errorText = "Napaka pri povezovanju s strežnikom"
        return
    print(playGame.board)
    uId = gui.readTextField(0)
    if uId == "":
        uniqueIDRequiered = True
        return
    uniqueIDRequiered = False
    gameCodeRequiered = False
    
    playGame.sendingAndReciving.unique_id = uId
    playGame.send_message("#CREATE", includeGameId=False)

    gui.startGame()
    playGame.play(gui)

def joinGame():
    global uniqueIDRequiered, gameCodeRequiered, errorText
    errorText = ""
    if not playGame.startSocket(playGame.board, playGame.legalMoves):
        errorText = "Napaka pri povezovanju s strežnikom"
        return
    uId = gui.readTextField(0)
    if uId == "":
        uniqueIDRequiered = True
        return
    uniqueIDRequiered = False
    playGame.sendingAndReciving.unique_id = uId
    gameCode = gui.readTextField(1)
    if gameCode == "":
        gameCodeRequiered = True
        return
    
    gameCodeRequiered = False
    playGame.sendingAndReciving.current_game_code = gameCode
    playGame.sendingAndReciving.validGameCode = "N/A"
    playGame.send_message("#JOIN")
    
    Thread(target=waitForGameCodeResponse).start()
    
gui.addText("Šah",(350,230),150,bold=True,isPermanent=True)
gui.addText("Unique ID",(385,570),40,bold=True,isPermanent=True)
gui.addTextField(5,410,610,bold=True,onlyNumbers=True)

gui.addText("Game Code",(370,650),40,bold=True,isPermanent=True)
gui.addTextField(5,410,690,bold=True)

gui.addButton("Create",createGame,(350,390),(200,60),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.RED,borderRadius=5,fontSize=18,bold=True,font="arial")
gui.addButton("Join",joinGame,(350,480),(200,60),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.RED,borderRadius=5,fontSize=18,bold=True,font="arial")

run = True
while run:
    gui.loadEvents()
    run=not gui.shouldQuit()
    gui.mouseClickedUpdate()     
    clicked = gui.buttonAndTextFieldCalculations()
    errorTextSize = getTextSize(errorText,40)
    gui.addText(errorText,(450-(errorTextSize/2),350),40,color=colors.RED,bold=True)

    if uniqueIDRequiered:
        gui.addText("UID REQUIRED",(550,570),40,color=colors.RED,bold=True)
    if gameCodeRequiered:
        gui.addText("GAME CODE REQUIRED",(550,650),40,color=colors.RED,bold=True)

    if startGameFlag:  # Preveri zastavico za začetek igre
        startGameFlag = False  # Ponastavi zastavico
        gui.startGame()
        playGame.play(gui)
        errorText = ""
        print("Game started")
    
    if playGame.sendingAndReciving.connectionError:
        playGame.sendingAndReciving.connectionError = False
        errorText = "Connection error"
        print("Connection error")

    gui.draw()