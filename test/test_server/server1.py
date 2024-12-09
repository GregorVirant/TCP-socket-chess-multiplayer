import socket
import threading
from cryptography.fernet import Fernet
import uuid

HOST = '127.0.0.1'
PORT = 1234  # Vrata strežnika
BUFFER_SIZE = 1024
running = True  # Če je True, potem strežnik posluša, sicer se konča

# Ključ za simetrično kriptiranje
key = "B8DRpjfj4ieG6zHMs7Ydn8O02MH8ZKnIMLCRoqvxFwA="
cipher_suite = Fernet(key)  # Ustvarjanje objekta za šifriranje in dešifriranje
s = None
games = {}  # {game_code: {'connections': [conn1, conn2], 'current_game': objekt od igre}}
games_lock = threading.Lock()  # Lock za sinhronizacijo dostopa do slovarja games

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
    with conn:
        while True:
            try:
                encrypted_message = conn.recv(BUFFER_SIZE)
                if not encrypted_message:
                    break
                message = cipher_suite.decrypt(encrypted_message).decode('utf-8')
                protocol, content = protocol_decode(message)
                protocol_check(protocol, content, conn)
            except Exception as e:
                print(f"Napaka pri obdelavi podatkov: {e}")
                break

def protocol_check(protocol, message, conn):
    if protocol == "#CREATE":
        game_code = str(uuid.uuid4())  # Ustvari nov edinstven game_code
        with games_lock:
            if game_code not in games:
                games[game_code] = {
                    'connections': [conn],
                    'game_state': None  # Inicializacija trenutnega stanja igre
                }
                print(f"Nova igra ustvarjena z game_code: {game_code}")  # Izpiši game_code v terminal
                send_response(conn, "#INFO", f"Igra ustvarjena z game_code: {game_code}. Čakamo na drugega igralca.")
            else:
                send_response(conn, "#ERROR", "Igra s to kodo že obstaja.")
    elif protocol == "#JOIN":
        game_code = message.strip()
        with games_lock:
            if game_code in games and len(games[game_code]['connections']) == 1:
                games[game_code]['connections'].append(conn)
                send_response(conn, "#INFO", "Pridružili ste se igri.")
                # Obvesti drugega igralca, da se je igralec pridružil
                opponent_conn = games[game_code]['connections'][0]
                send_response(opponent_conn, "#INFO", "Drugi igralec se je pridružil. Igra se lahko začne.")
            else:
                send_response(conn, "#ERROR", "Igre ni mogoče najti ali je že polna.")
    elif protocol == "#M":
        # Pričakuje se, da je message v obliki 'game_code:actual_message'
        try:
            game_code, actual_message = message.split(":", 1)
            with games_lock:
                if game_code in games:
                    # Pošlji sporočilo drugemu igralcu
                    for player_conn in games[game_code]['connections']:
                        if player_conn != conn:
                            send_response(player_conn, "#M", actual_message)
                else:
                    send_response(conn, "#ERROR", "Igre ni mogoče najti.")
        except ValueError:
            send_response(conn, "#ERROR", "Neveljavno sporočilo.")
    elif protocol == "#EXIT":
        game_code = message.strip()
        with games_lock:
            if game_code in games:
                games[game_code]['connections'].remove(conn)
                if not games[game_code]['connections']:
                    del games[game_code]
                send_response(conn, "#INFO", "Izhod iz igre.")
            else:
                send_response(conn, "#ERROR", "Igre ni mogoče najti.")
    else:
        send_response(conn, "#ERROR", "Neznan protokol.")

def send_response(conn, protocol, message):
    try:
        full_message = protocol_encode(protocol, message)
        encrypted_response = cipher_suite.encrypt(full_message.encode('utf-8'))
        conn.sendall(encrypted_response)
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
