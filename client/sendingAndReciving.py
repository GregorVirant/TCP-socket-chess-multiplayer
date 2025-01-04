import copy
import socket
import threading
import ast
import time

SERVER_IP = '127.0.0.1'
PORT = 1235
BUFFER_SIZE = 1024


current_game_code = None
unique_id = None
clientSocket = None
board = None
legalMoves = None
isWhiteTurn = True
amIWhite = None
Time = "10:0:0 - 10:0:0"
timerStarted = False

timerThread = None
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
            messages = splitIfPossible(decrypted_data)
            for mes in messages:
                protocol, message = protocol_decode(mes)
                handle_server_response(protocol, message)
        except Exception as e:
            print(f"Napaka pri prejemanju podatkov: {e}")
            break

def handle_server_response(protocol, message):
    global current_game_code, board, legalMoves, isWhiteTurn, Time, timerStarted, amIWhite, timerThread
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
        if message == "True":
            isWhiteTurn = True
        else:
            isWhiteTurn = False
    elif protocol == "#AMWHITE":
        if message == "True":
            amIWhite = True
        else:
            amIWhite = False
    elif protocol == "#END":
        print(f"END: {message}")
        timerStarted = False
        if timerThread:
            timerThread.join()
        Time = "10:0:0 - 10:0:0"

    elif protocol == "#LEGALMOVES":
        legalMoves2 = ast.literal_eval(message)
        for i in range(8):
            for j in range(8):
                legalMoves[i][j] = legalMoves2[i][j]
        print(f"LEGALMOVES: {legalMoves}")
    elif protocol == "#TIME":
        if amIWhite:
            myTime, enemyTime = message.split(":")
        else:
            enemyTime, myTime = message.split(":")
        Time = f"{toMinutesAndSeconds(myTime)} - {toMinutesAndSeconds(enemyTime)}"
        print(Time)
        if not timerStarted:
            timerStarted = True
            timerThread = threading.Thread(target=start_timer, daemon=True)
            timerThread.start()

    else:
        print(f"Neznana koda: {protocol} - {message}")

def toMinutesAndSeconds(time):
    time = float(time)
    minutes = int(time // 60)
    seconds = int(time % 60)
    tenths = int((time - int(time)) * 10)
    rez = f"{minutes}:{seconds}:{tenths}"
    return rez
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
def splitIfPossible(message):
    try:
        message = message.split("#/|/#")
        if message[-1] == "":
            message.pop()
        return message
    except:
        return message
def protocol_encode(protocol, message):
    return f"{protocol}/|/{message}"

def protocol_decode(message):
    try:
        protocol, content = message.split("/|/", 1)
        return protocol, content
    except Exception as e:
        print("Napaka pri dekodiranju sporočila:", e)
        return None, None
    
def start_timer():
    global Time, isWhiteTurn, amIWhite, timerStarted
    while timerStarted:
        time.sleep(1)
        myTime, enemyTime = Time.split(" - ")
        if (isWhiteTurn and amIWhite) or (not isWhiteTurn and not amIWhite):
            myTime = decrement_time(myTime)
        else:
            enemyTime = decrement_time(enemyTime)
        Time = f"{myTime} - {enemyTime}"

def decrement_time(timeStr):
    minutes, seconds, tenths = map(int, timeStr.split(":"))
    totalSeconds = minutes * 60 + seconds + tenths / 10.0
    totalSeconds -= 1
    if totalSeconds < 0:
        totalSeconds = 0
    minutes = int(totalSeconds // 60)
    seconds = int(totalSeconds % 60)
    tenths = int((totalSeconds - int(totalSeconds)) * 10)
    return f"{minutes}:{seconds}:{tenths}"