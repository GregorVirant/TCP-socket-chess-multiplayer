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
    global errorText, startGameFlag
    errorText = "Waiting for server response"
    for i in range(31):
        if i == 30:
            errorText = "No response from server"
            return
        elif playGame.sendingAndReciving.isThereNoErrors == "N/A":
            pass
        elif playGame.sendingAndReciving.isThereNoErrors == "True":
            startGameFlag = True  # Nastavi zastavico za začetek igre
            break
        elif playGame.sendingAndReciving.isThereNoErrors == "False":
            errorText = "Invalid game code"
            return
        elif playGame.sendingAndReciving.isThereNoErrors == "Duplicate":
            errorText = "Duplicate user id"
            return
        elif playGame.sendingAndReciving.isThereNoErrors == "Full":
            errorText = "Game is full"
            return
        else:
            return
        sleep(0.1)



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
    playGame.sendingAndReciving.isThereNoErrors = "N/A"
    playGame.send_message("#JOIN")
    
    Thread(target=waitForGameCodeResponse,daemon = True).start()
    
#gui.addText("Šah",(350,230),150,bold=True,isPermanent=True)
gui.addText("Unique ID",(335+gui.borderWidth,600),40,bold=True,isPermanent=True)
gui.addTextField(5,360+gui.borderWidth,640,bold=True,onlyNumbers=True)

gui.addText("Game Code",(320+gui.borderWidth,680),40,bold=True,isPermanent=True)
gui.addTextField(5,360+gui.borderWidth,720,bold=True)

gui.addButton("Create",createGame,(300+gui.borderWidth,420),(200,60),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.RED,borderRadius=5,fontSize=18,bold=True,font="arial")
gui.addButton("Join",joinGame,(300+gui.borderWidth,510),(200,60),buttonColor=colors.LIGHT_PURPLE,hoverColor=colors.RED,borderRadius=5,fontSize=18,bold=True,font="arial")

run = True
while run:
    gui.loadEvents()
    run=not gui.shouldQuit()
    gui.mouseClickedUpdate()     
    clicked = gui.buttonAndTextFieldCalculations()
    errorTextSize = gui.getTextSize(errorText,40)
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