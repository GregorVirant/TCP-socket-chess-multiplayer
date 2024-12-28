import copy
import socket
import threading
import ast

SERVER_IP = '127.0.0.1'
PORT = 1235
BUFFER_SIZE = 1024


current_game_code = None
unique_id = None
clientSocket = None
board = None
legalMoves = None
isWhiteTurn = None
amIWhite = None

def startSocket(board1, legalMoves1):
    global clientSocket, board, legalMoves, amIWhite, isWhiteTurn
    legalMoves = legalMoves1
    board = board1

    
    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((SERVER_IP, PORT))
    except Exception as e:
        print("Napaka pri povezovanju s strežnikom:", e)
        return False
    threading.Thread(target=listen_to_server, args=(clientSocket,None), daemon=True).start()
    return True

def setGameCode(gameCode):
    global current_game_code
    current_game_code = gameCode

def closeConnection():
    global current_game_code
    print("Zapiram povezavo")
    sporocilo = f"{current_game_code}:{unique_id}"
    send_message("#EXIT", sporocilo)
    current_game_code = None
    if clientSocket:
        clientSocket.close()

def listen_to_server(client,tmp):
    while True:
        try:
            encrypted_data = client.recv(BUFFER_SIZE)
            if not encrypted_data:
                break
            decrypted_data = encrypted_data.decode()
            protocol, message = protocol_decode(decrypted_data)
            handle_server_response(protocol, message)
        except Exception as e:
            print(f"Napaka pri prejemanju podatkov: {e}")
            break

def handle_server_response(protocol, message):
    global current_game_code, board, legalMoves
    print(f"Prejeto: {protocol} - {message}")
    if protocol == "#INFO":
        print(f"INFO: {message}")
        if "Igra je bila ustvarjena" in message:
            current_game_code = message.split("Koda igre: ")[1]
    elif protocol == "#ERROR":
        print(f"NAPAKA: {message}")
    elif protocol == "#M":
        print(f"SPOROČILO: {message}")
    elif protocol == "#GAMEID":
        current_game_code = message
    elif protocol == "#BOARD":
        board2 = ast.literal_eval(message)
        for i in range(8):
            for j in range(8):
                board[i][j] = board2[i][j]
        print(f"BOARD: {board}")
    elif protocol == "#TURN":
        print(f"TURN: {message}")
    elif protocol == "#END":
        print(f"END: {message}")
    elif protocol == "#LEGALMOVES":
        legalMoves2 = ast.literal_eval(message)
        for i in range(8):
            for j in range(8):
                legalMoves[i][j] = legalMoves2[i][j]
        print(f"LEGALMOVES: {legalMoves}")
    else:
        print(f"Neznana koda: {protocol} - {message}")

def send_message(protocol, includeGameId=True, message=None):
    try:
        if includeGameId:
            if message == None:
                full_message = f"{current_game_code.lower()}:{unique_id}"
            else:
                full_message = f"{current_game_code.lower()}:{unique_id}:{message}"
        else:
            full_message = f"{unique_id}"
        encoded_message = protocol_encode(protocol, full_message)
        encrypted_message = encoded_message.encode()
        clientSocket.sendall(encrypted_message)
    except Exception as e:
        print(f"Napaka pri pošiljanju: {e}")

def protocol_encode(protocol, message):
    return f"{protocol}/|/{message}"

def protocol_decode(message):
    try:
        protocol, content = message.split("/|/", 1)
        return protocol, content
    except Exception as e:
        print("Napaka pri dekodiranju sporočila:", e)
        return None, None