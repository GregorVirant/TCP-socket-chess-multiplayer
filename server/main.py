#MAIN SERVER
import uuid
import game
import threading
import socket

HOST = '127.0.0.1'
PORT = 1234  # Vrata strežnika
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
                protocol, data = protocol_decode(data)
                if connectedToGame:
                    protocol_check_ME(protocol, data, conn) # za sporočila in exit
                else:
                    connectedToGame = protocol_check_CJ(protocol, data, conn) # za create in join

            except Exception as e:
                print(f"Napaka pri obdelavi podatkov: {e}")
                break

def protocol_check_CJ(protocol, message, conn):  # za create in join
    if protocol == "#CREATE": # Format: #CREATE/|/uniqueID
        game_code = str(uuid.uuid4())
        with lock:
            createdMatch = game.Game(game_code, conn, message)  # message contains uniqueID
            games.append(createdMatch)
            send_response(conn, "#GAMEID", game_code)
            print(f"Ustvarjena igra z id: {game_code}")
            send_response(conn, "#INFO", f"Igra je bila ustvarjena. Koda igre: {game_code}")
            return True
    elif protocol == "#JOIN":  # Format: game_code:uniqueID
        try:
            game_code, unique_id = message.strip().split(":", 1)
            with lock:
                for match in games:
                    if match.gameID == game_code:
                        # če se hoče kdo reconnectat
                        if match.isPlayerReconnecting(unique_id):
                            match.reconnectPlayer(conn, unique_id)
                            print(f"Igralec {unique_id} se je ponovno povezal v igro {game_code}")
                            send_response(conn, "#INFO", f"Ponovno ste se povezali v igro {game_code}")
                            return True
                        # če se drugi pridružit igri
                        elif match.isOneSpaceEmpty():
                            match.addPlayer2(conn, unique_id)
                            print(f"Igralec {unique_id} se je pridružil igri {game_code}")
                            send_response(conn, "#INFO", f"Pridružili ste se igri {game_code}")
                            return True
                        else:
                            send_response(conn, "#ERROR", "Igra je že polna.")
                            return False
                send_response(conn, "#ERROR", "Igre ni mogoče najti.")
        except ValueError:
            send_response(conn, "#ERROR", "Neveljavno sporočilo. Format: game_code:uniqueID")
    return False
    
def protocol_check_ME(protocol, message, conn): # za sporočila in exit
    if protocol == "#M":  # Format: game_code:message
        try:
            game_code, actual_message = message.split(":", 1)
            with lock:
                for match in games:
                    if match.gameID == game_code:
                        print(f"Sporočilo poslano v igri {game_code}: {actual_message}")
                        if match.socketC1 is not None:
                            send_response(match.socketC1, "#M", actual_message)
                        if match.socketC2 is not None:
                            send_response(match.socketC2, "#M", actual_message)
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

def send_response(conn, protocol, message):
    try:
        message = protocol_encode(protocol, message)
        conn.sendall(message.encode('utf-8'))
    except Exception as e:
        print("Napaka pri pošiljanju podatkov:", e)

def protocol_encode(protocol, message):
    return f"{protocol}/|/{message}"

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

if __name__ == "__main__":
    main()