#MAIN ODJEMALEC
from gui import *
import playGame
from playGame import gui

run = True
gui.loadNextTexture() #loads figure textures (folder for textures, figures scale)

uniqueIDRequiered = False
gameCodeRequiered = False

def createGame():
    global uniqueIDRequiered, gameCodeRequiered
    playGame.startSocket(playGame.board, playGame.legalMoves)
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
    global uniqueIDRequiered, gameCodeRequiered
    playGame.startSocket(playGame.board, playGame.legalMoves)

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
    #print(f"JOIN GAME | UID:{uId} | GAME ID: {gameCode}")
    playGame.sendingAndReciving.current_game_code = gameCode
    playGame.send_message("#JOIN")
    gui.startGame()
    playGame.play(gui)
gui.addText("Šah",(350,230),150,bold=True,isPermanent=True)
#print(gui.textImagesPermanent)
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

    if uniqueIDRequiered:
        gui.addText("UID REQUIRED",(550,570),40,color=colors.RED,bold=True)
    if gameCodeRequiered:
        gui.addText("GAME CODE REQUIRED",(550,650),40,color=colors.RED,bold=True)

    gui.draw()


# """
# Protokoli:
# - pošiljanje:
#     - #CREATE/|/uniqueID
#     - #JOIN/|/game_code:uniqueID
#     - #M/|/game_code:message
#     - #EXIT/|/game_code:uniqueID
# - prejemanje:
#     - #INFO
#     - #ERROR
#     - #M (message)
# """

# from cryptography.fernet import Fernet
# import socket
# import threading
# import uuid

# SERVER_IP = '127.0.0.1'
# PORT = 1234
# BUFFER_SIZE = 1024


# current_game_code = None
# unique_id = None
# running = True

# def main():
#     global current_game_code, unique_id, running

#     #unique_id = str(uuid.uuid4())  # Generate unique ID for this client
    
#     try:
#         client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         client.connect((SERVER_IP, PORT))
#     except Exception as e:
#         print("Napaka pri povezovanju s strežnikom:", e)
#         return
#     unique_id = input("Vnesite ID: ")
#     threading.Thread(target=listen_to_server, args=(client,), daemon=True).start()

#     try:
#         while running:
#             print("\nIzberite možnost:")
#             if current_game_code is None:
#                 print("1. Ustvari igro")
#                 print("2. Pridruži se igri")
#             print("3. Pošlji sporočilo")
#             print("4. Zapusti igro")
#             choice = input("Vnos: ")

#             if choice == '1' and current_game_code is None:
#                 send_message("#CREATE", client, unique_id)
#             elif choice == '2' and current_game_code is None:
#                 game_code = input("Vnesite kodo igre za pridružitev: ")
#                 current_game_code = game_code
#                 send_message("#JOIN", client, f"{game_code}:{unique_id}")
#             elif choice == '3':
#                 if current_game_code is not None:
#                     message = input("Vnesite sporočilo: ")
#                     send_message("#M", client, f"{current_game_code}:{message}")
#                 else:
#                     print("Niste povezani z nobeno igro.")
#             elif choice == '4':
#                 if current_game_code is not None:
#                     print(current_game_code)
#                     sporocilo = f"{current_game_code}:{unique_id}"
#                     send_message("#EXIT", client, sporocilo)
#                     current_game_code = None
#                     client.close()
#                     running = False
#                 else:
#                     print("Niste povezani z nobeno igro.")

#     except KeyboardInterrupt:
#         print("\nZapiram povezavo...")
#     finally:
#         client.close()

# def listen_to_server(client):
#     while True:
#         try:
#             encrypted_data = client.recv(BUFFER_SIZE)
#             if not encrypted_data:
#                 break
#             decrypted_data = encrypted_data.decode()
#             protocol, message = protocol_decode(decrypted_data)
#             handle_server_response(protocol, message)
#         except Exception as e:
#             print(f"Napaka pri prejemanju podatkov: {e}")
#             break

# def handle_server_response(protocol, message):
#     global current_game_code
#     if protocol == "#INFO":
#         print(f"INFO: {message}")
#         if "Igra je bila ustvarjena" in message:
#             current_game_code = message.split("Koda igre: ")[1]
#     elif protocol == "#ERROR":
#         print(f"NAPAKA: {message}")
#     elif protocol == "#M":
#         print(f"SPOROČILO: {message}")
#     elif protocol == "#GAMEID":
#         current_game_code = message

# def send_message(protocol, client, message):
#     try:
#         encoded_message = protocol_encode(protocol, message)
#         encrypted_message = encoded_message.encode()
#         client.sendall(encrypted_message)
#     except Exception as e:
#         print(f"Napaka pri pošiljanju: {e}")

# def protocol_encode(protocol, message):
#     return f"{protocol}/|/{message}"

# def protocol_decode(message):
#     try:
#         protocol, content = message.split("/|/", 1)
#         return protocol, content
#     except Exception as e:
#         print("Napaka pri dekodiranju sporočila:", e)
#         return None, None

# if __name__ == "__main__":
#     main()