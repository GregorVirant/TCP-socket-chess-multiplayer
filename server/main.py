#MAIN SERVER
import uuid
import game
import threading
import socket
from time import sleep

HOST = '127.0.0.1'
PORT = 1235  # Vrata strežnika
BUFFER_SIZE = 1024
running = True  # Če je True, potem strežnik posluša, sicer se konča
s = None

games = []
lock = threading.Lock()

def main():
    global s  # Dovoljenje za spreminjanje globalnega socketa
    threading.Thread(target=wait_exit, args=(), daemon=True).start()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((HOST, PORT))
            s.listen()
        except Exception as e:
            print(f"Napaka pri zagonu strežnika: {e}")
            return 1

        print("Strežnik posluša na: ", PORT)
        while running:
            try:
                conn, addr = s.accept()
                threading.Thread(target=handle_client, args=(conn,), daemon=True).start()
            except OSError:
                break
            except Exception as e:
                print(f"Napaka pri sprejemanju povezave: {e}")

def handle_client(conn):
    connectedToGame = False
    with conn:
        while True:
            try:
                if not conn:
                    break
                data = conn.recv(BUFFER_SIZE)
            
                if not data:
                    break
                data = data.decode()
                data = splitIfPossible(data)
                for message in data:
                    protocol, data = protocol_decode(message)
                if connectedToGame:
                    protocol_check_other(protocol, data, conn) # za sporočila in exit
                else:
                    connectedToGame = protocol_check_CJ(protocol, data, conn) # za create in join

            except Exception as e:
                print(f"Napaka pri obdelavi podatkov: {e}")
                break

def protocol_check_CJ(protocol, message, conn):  # za create in join
    if protocol == "#CREATE": # Format: #CREATE/|/uniqueID
        game_code = str(uuid.uuid4())[:5]
        with lock:
            tempBoard = None
            createdMatch = game.Game(game_code, conn, message)  # message contains uniqueID
            games.append(createdMatch)
            send_response(conn, "#GAMEID", game_code)
            sleep(1)
            tempBoard = createdMatch.chessBoard
            if createdMatch.whoIsWhite == 2:
                tempBoard = createdMatch.flipBoard()
            send_response(conn, "#BOARD", tempBoard)
            print(f"Ustvarjena igra z id: {game_code}")
            send_response(conn, "#INFO", f"Igra je bila ustvarjena. Koda igre: {game_code}")
            send_response(conn, "#AMWHITE", "True" if createdMatch.whoIsWhite == 1 else "False")
            threading.Thread(target=checkIfNoTime, args=(game_code,), daemon=True).start()
            return True
    elif protocol == "#JOIN":  # Format: game_code:uniqueID
        try:
            game_code, unique_id = message.strip().split(":", 1)
            game_code = game_code.lower()
            tempBoard = None
            with lock:
                for match in games:
                    if match.gameID == game_code:
                        
                        # preveri, če je igralčev unique_id že v igri
                        if match.isDuplicateId(unique_id):
                            send_response(conn, "#ISNOERRORS", "Duplicate")
                            print(f"Duplicate")
                            return False
                        
                        # če se hoče kdo reconnectat
                        if match.isPlayerReconnecting(unique_id):
                            match.reconnectPlayer(conn, unique_id)
                            send_response(conn, "#ISNOERRORS", True)

                            print(f"Igralec {unique_id} se je ponovno povezal v igro {game_code}")
                            send_response(conn, "#INFO", f"Ponovno ste se povezali v igro {game_code}")
                           
                            sleep(1)
                            
                            tempBoard = match.chessBoard
                            match.updateBoard()
                            if match.whoIsWhite != match.getPlayerNumber(unique_id):
                                tempBoard = match.flipBoard()
                            send_response(conn, "#BOARD", tempBoard)
                            send_response(conn, "#AMWHITE", "True" if match.whoIsWhite == match.getPlayerNumber(unique_id) else "False")
                            return True
                        # če se drugi pridružit igri
                        elif match.isOneSpaceEmpty():
                            send_response(conn, "#ISNOERRORS", True)
                            match.addPlayer2(conn, unique_id)
                            print(f"Igralec {unique_id} se je pridružil igri {game_code}")
                            send_response(conn, "#INFO", f"Pridružili ste se igri {game_code}")
                            sleep(1)
                            tempBoard = match.chessBoard
                            if match.whoIsWhite == 1:
                                tempBoard = match.flipBoard()
                            send_response(conn, "#BOARD", tempBoard)
                            send_response(conn, "#AMWHITE", "True" if match.whoIsWhite == 2 else "False")

                            send_response(match.socketC1,"#GSTART","")
                            send_response(conn,"#GSTART","")

                            match.start = True

                            return True
                        else:
                            send_response(conn, "#ISNOERRORS", "Full")
                            send_response(conn, "#ERROR", "Igra je že polna.")
                            return False
                send_response(conn, "#ERROR", "Igre ni mogoče najti.")
                send_response(conn, "#ISNOERRORS", False)
        except ValueError:
            send_response(conn, "#ERROR", "Neveljavno sporočilo. Format: game_code:uniqueID")
    return False
    
def protocol_check_other(protocol, message, conn): # za sporočila in exit
    global games
    if protocol == "#PING":
        pass
    elif protocol == "#MESSAGE":  # Format: game_code:message
        try:
            game_code, actual_message = message.split(":", 1)
            with lock:
                for match in games:
                    if match.gameID == game_code:
                        print(f"Sporočilo poslano v igri {game_code}: {actual_message}")
                        if match.socketC1 is not None:
                            send_response(match.socketC1, "#BOARD", actual_message)
                        if match.socketC2 is not None:
                            send_response(match.socketC2, "#BOARD", actual_message)
                        return
                send_response(conn, "#ERROR", "Igre ni mogoče najti.")
        except ValueError:
            send_response(conn, "#ERROR", "Neveljavno sporočilo. Format: game_code:message")
    elif protocol == "#EXIT":  # Format: game_code:uniqueID
        try:
            game_code, unique_id = message.strip().split(":", 1)
            print(f"Zahteva za izhod iz igre {game_code} od igralca {unique_id}")
            with lock:
                for match in games:
                    if match.gameID == game_code:
                        print(f"Najdena igra {game_code}")
                        match.disconnectPlayer(unique_id)
                        conn.close()
                        print(f"Igralec {unique_id} se je odjavil iz igre {game_code}")
                        # Check if game is empty
                        if match.isEmpty():
                            games.remove(match)
                            print(f"Igra {game_code} je bila odstranjena.")
                        return
                print(f"Igra {game_code} ni bila najdena")
                send_response(conn, "#ERROR", "Igre ni mogoče najti.")
        except ValueError:
            print("Napaka pri obdelavi EXIT sporočila")
            send_response(conn, "#ERROR", "Neveljavno sporočilo. Format: game_code:uniqueID")
    elif protocol == "#GETLEGALMOVES": # Format: game_code:uniqueID:row:column
        try:
            game_code, unique_id, row, column = message.strip().split(":", 3)
            print(row, column)
            with lock:
                for match in games:
                    if match.gameID == game_code:
                        if not match.start:
                            send_response(conn, "#ERROR", "Igra se še ni začela.")
                            return                             
                        if not match.isPlayerTurn(unique_id):
                            send_response(conn, "#ERROR", "Nisi na vrsti.")
                            return

                        print(f"Zahteva za legalne poteze v igri {game_code} od igralca {unique_id}")
                        if match.socketC1 is not None and match.uniqueCodeC1 == unique_id:
                            if match.whoIsWhite != 1:
                                row = 7 - int(row)
                                column = 7 - int(column)
                            legalMoves = match.getLegalMoves(int(row), int(column))
                            legalMoves1 = legalMoves
                            if match.whoIsWhite != 1:
                                legalMoves1 = match.flipLegalMoves(legalMoves)
                            send_response(match.socketC1, "#LEGALMOVES", legalMoves1)
                            print(f"Legalne poteze poslane igralcu {unique_id}")
                        elif match.socketC2 is not None and match.uniqueCodeC2 == unique_id:
                            if match.whoIsWhite != 2:
                                row = 7 - int(row)
                                column = 7 - int(column)
                            legalMoves = match.getLegalMoves(int(row), int(column))
                            legalMoves1 = legalMoves
                            if match.whoIsWhite != 2:
                                legalMoves1 = match.flipLegalMoves(legalMoves)
                                print(legalMoves1)
                            send_response(match.socketC2, "#LEGALMOVES", legalMoves1)
                            print(f"Legalne poteze poslane igralcu {unique_id}")
                        else:
                            send_response(conn, "#ERROR", "Igralec ni v igri.")
                        return
                send_response(conn, "#ERROR", "Igre ni mogoče najti.")
        except ValueError:
            print("Napaka pri obdelavi GETLEGALMOVES sporočila")
            send_response(conn, "#ERROR", "Neveljavno sporočilo. Format: row:column")
    elif protocol == "#MOVE":
        try:
            print(f"MESSAGE: {message}")
            parts = message.strip().split(":", 6)
            #print(message)
            if len(parts) == 6:
                game_code, unique_id, startRow, startCol, endRow, endCol = parts
                piece = None
            else:
                #print(parts)
                game_code, unique_id, startRow, startCol, endRow, endCol, piece = parts
            with lock:
                for match in games:
                    if match.gameID == game_code:
                        if not match.start:
                            send_response(conn, "#ERROR", "Igra se še ni začela.")
                            return      
                        if match.chess.promoting:
                            match.isWhiteTurn = not match.isWhiteTurn
                            if not match.isPlayerTurn(unique_id):
                                send_response(conn, "#ERROR", "Nisi na vrsti.1")
                                return

                            piece = int(piece)
                            startRow = int(startRow)
                            startCol = int(startCol)
                            endRow = int(endRow)
                            endCol = int(endCol)
                            if not match.isWhiteTurn: 
                                piece = -piece 

                                startRow = 7 - startRow
                                startCol = 7 - startCol
                                endRow = 7 - endRow
                                endCol = 7 - endCol
                            print(f"PROMOTE TO {piece}")
                            match.chess.currBoard[endRow][endCol] = piece
                            #return

                            board1 = match.chessBoard
                            board2 = match.chessBoard
                            if match.whoIsWhite == 1:
                                board2 = match.flipBoard()
                            else:
                                board1 = match.flipBoard()
                            if match.socketC1 is not None and match.uniqueCodeC1 == unique_id:
                                send_response(match.socketC1, "#TURN", str(match.isWhiteTurn))
                                send_response(match.socketC1, "#BOARD", board1)
                                send_response(match.socketC1, "#INFO", "Poteza uspešno narejena.")
                                if match.socketC2 is not None:
                                    send_response(match.socketC2, "#TURN", str(match.isWhiteTurn))
                                    send_response(match.socketC2, "#BOARD", board2)
                                    send_response(match.socketC2, "#INFO", "Nasprotnik je naredil potezo.")
                            elif match.socketC2 is not None and match.uniqueCodeC2 == unique_id:
                                send_response(match.socketC2, "#TURN", str(match.isWhiteTurn))
                                send_response(match.socketC2, "#BOARD", board2)
                                send_response(match.socketC2, "#INFO", "Poteza uspešno narejena.")
                                if match.socketC1 is not None:
                                    send_response(match.socketC1, "#TURN", str(match.isWhiteTurn))
                                    send_response(match.socketC1, "#BOARD", board1)
                                    send_response(match.socketC1, "#INFO", "Nasprotnik je naredil potezo.")
                            print(f"Legalne poteze poslane igralcu {unique_id}")
                            send_response(match.socketC1, "#TIME", f"{match.timeWhite}:{match.timeBlack}")
                            send_response(match.socketC2, "#TIME", f"{match.timeWhite}:{match.timeBlack}")
                            match.isWhiteTurn = not match.isWhiteTurn
                            match.chess.promoting = False


                        else:
                            if not match.isPlayerTurn(unique_id):
                                send_response(conn, "#ERROR", "Nisi na vrsti.")
                                return
                            if match.whoIsWhite != match.getPlayerNumber(unique_id):
                                startRow = 7 - int(startRow)
                                startCol = 7 - int(startCol)
                                endRow = 7 - int(endRow)
                                endCol = 7 - int(endCol)
                            #print("BOARD:" + str(match.chessBoard))
                            print(startRow, startCol, endRow, endCol)
                            legalMoves = match.chess.getLegalMoves(int(startRow), int(startCol))
                            if legalMoves[int(endRow)][int(endCol)] in (2, 3):
                                notation = match.generateMoveNotation(int(startRow), int(startCol), int(endRow), int(endCol))
                                moveMade = match.makeMove((int(startRow), int(startCol)), (int(endRow), int(endCol)))
                                if moveMade == False:
                                    send_response(conn, "#ERROR", "Neveljavna poteza.")
                                    return
                                if match.chess.isCheck(match.chess.isWhiteToMove):
                                    notation += "+"
                                if match.chess.isMate():
                                  notation += "#"

                                
                                if match.chess.promoting:                
                                    send_response(conn, "#PROMO",message)
                                    return
                                
                                match.moves.append(notation)
                                match.saveToFile()
                                print(notation)
                                print("BOARD:" + str(match.chessBoard))
                                print(f"Igralec {unique_id} je naredil potezo v igri {game_code}")
                                match.updateBoard()
                                board1 = match.chessBoard
                                board2 = match.chessBoard
                                if match.whoIsWhite == 1:
                                    board2 = match.flipBoard()
                                else:
                                    board1 = match.flipBoard()
                                if match.socketC1 is not None and match.uniqueCodeC1 == unique_id:
                                    send_response(match.socketC1, "#TURN", str(match.isWhiteTurn))
                                    send_response(match.socketC1, "#BOARD", board1)
                                    send_response(match.socketC1, "#INFO", "Poteza uspešno narejena.")
                                    send_response(match.socketC1, "#MOVEMADE", f"{startRow}:{startCol}:{endRow}:{endCol}")
                                    if match.socketC2 is not None:
                                        send_response(match.socketC2, "#TURN", str(match.isWhiteTurn))
                                        send_response(match.socketC2, "#BOARD", board2)
                                        send_response(match.socketC2, "#INFO", "Nasprotnik je naredil potezo.")
                                        send_response(match.socketC2, "#MOVEMADE", f"{startRow}:{startCol}:{endRow}:{endCol}")
                                elif match.socketC2 is not None and match.uniqueCodeC2 == unique_id:
                                    send_response(match.socketC2, "#TURN", str(match.isWhiteTurn))
                                    send_response(match.socketC2, "#BOARD", board2)
                                    send_response(match.socketC2, "#INFO", "Poteza uspešno narejena.")
                                    send_response(match.socketC2, "#MOVEMADE", f"{startRow}:{startCol}:{endRow}:{endCol}")
                                    if match.socketC1 is not None:
                                        send_response(match.socketC1, "#TURN", str(match.isWhiteTurn))
                                        send_response(match.socketC1, "#BOARD", board1)
                                        send_response(match.socketC1, "#INFO", "Nasprotnik je naredil potezo.")
                                        send_response(match.socketC1, "#MOVEMADE", f"{startRow}:{startCol}:{endRow}:{endCol}")
                                print(f"Legalne poteze poslane igralcu {unique_id}")
                                send_response(match.socketC1, "#TIME", f"{match.timeWhite}:{match.timeBlack}")
                                send_response(match.socketC2, "#TIME", f"{match.timeWhite}:{match.timeBlack}")
                            else:
                                send_response(conn, "#ERROR", "Neveljavna poteza.")
                    else:
                        send_response(conn, "#ERROR", "Igre ni mogoče najti.")
        except ValueError:
            print("Napaka pri obdelavi MOVE sporočila")
            send_response(conn, "#ERROR", "Neveljavno sporočilo. Format: startRow:startCol:endRow:endCol")
    elif protocol == "#SURRENDER":
        try:
            game_code, unique_id = message.strip().split(":", 1)
            with lock:
                for match in games:
                    if match.gameID == game_code:
                        if not match.start:
                            send_response(conn, "#ERROR", "Igra se še ni začela.")
                            return      
                        if match.uniqueCodeC1 == unique_id:
                            send_response(match.socketC2, "#END", "Nasprotnik se je predal.")
                            send_response(match.socketC1, "#END", "Predali ste se.")
                        elif match.uniqueCodeC2 == unique_id:
                            send_response(match.socketC1, "#END", "Nasprotnik se je predal.")
                            send_response(match.socketC2, "#END", "Predali ste se.")

                        # match.resetGame()
                        # if match.whoIsWhite == 1:
                        #     send_response(match.socketC1, "#BOARD", match.chessBoard)
                        #     send_response(match.socketC2, "#BOARD", match.flipBoard())
                        # else:
                        #     send_response(match.socketC1, "#BOARD", match.flipBoard())
                        #     send_response(match.socketC2, "#BOARD", match.chessBoard)

                        # send_response(match.socketC1, "#AMWHITE", "True" if match.whoIsWhite == 1 else "False")
                        # send_response(match.socketC2, "#AMWHITE", "True" if match.whoIsWhite == 2 else "False")

                        print(f"Igralec {unique_id} se je predal v igri {game_code}")
                        return
                send_response(conn, "#ERROR", "Igre ni mogoče najti.")
        except ValueError:
            print("Napaka pri obdelavi SURRENDER sporočila")
            send_response(conn, "#ERROR", "Neveljavno sporočilo. Format: game_code:uniqueID")
    

def send_response(conn, protocol, message):
    try:
        message = protocol_encode(protocol, message) + "#/|/#"
        conn.sendall(message.encode('utf-8'))
    except Exception as e:
        print("Napaka pri pošiljanju podatkov:", e)

def protocol_encode(protocol, message):
    return f"{protocol}/|/{message}"

def splitIfPossible(message):
    try:
        message = message.split("#/|/#")
        if message[-1] == "":
            message.pop()
        return message
    except:
        return message
    
def protocol_decode(message):
    try:
        protocol, content = message.split("/|/", 1)
        return protocol, content
    except Exception as e:
        print("Napaka pri dekodiranju sporočila:", e)
        return None, None

def wait_exit():  # Zaustavitev strežnika z ukazom 'exit'
    global running, s
    while True:
        message = input("Za izhod vnesite 'exit'!\n")
        if message.lower() == 'exit':
            print("Ugasnil sem strežnik.")
            running = False
            if s:
                s.close()  # Zapiranje socketa
            break

def checkIfNoTime(gameid):
    for match in games:
        if match.gameID == gameid:
            while match.isRunning:
                isNoTime = match.checkTime()
                if isNoTime == "B":
                    send_response(match.socketC1, "#END", "Nasprotniku je zmanjkalo časa.")
                    send_response(match.socketC2, "#END", "Čas vam je potekel.")
                    break
                elif isNoTime == "W":
                    send_response(match.socketC1, "#END", "Čas vam je potekel.")
                    send_response(match.socketC2, "#END", "Nasprotniku je zmanjkalo časa.")
                    break
                sleep(1)
    return None
    

if __name__ == "__main__":
    main()