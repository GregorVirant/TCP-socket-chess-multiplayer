import socket
import threading
from cryptography.fernet import Fernet

SERVER_IP = "127.0.0.1"  # IP naslov strežnika
PORT = 1234  # Vrata strežnika
BUFFER = 1024  # Medpomnilnik za prejemanje podatkov

# Ključ za simetrično kriptiranje
key = "B8DRpjfj4ieG6zHMs7Ydn8O02MH8ZKnIMLCRoqvxFwA="
cipher_suite = Fernet(key)

current_game_code = None  # Trenutna koda igre

def main():
    global current_game_code
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP/IP vtičnica
        client.connect((SERVER_IP, PORT))  # Povezava s strežnikom
    except Exception as e:
        print("Napaka pri povezovanju s strežnikom:", e)
        return
    threading.Thread(target=listen_to_server, args=(client,), daemon=True).start()

    try:
        while True:
            print("Izberite možnost:")
            if current_game_code is None:
                print("1. Ustvari igro")
                print("2. Pridruži se igri")
            print("3. Pošlji sporočilo")
            print("4. Zapusti igro")
            choice = input("Vnos: ")

            if choice == '1' and current_game_code is None:
                game_code = input("Vnesite kodo igre za ustvarjanje: ")
                send_message("#CREATE", client, game_code)
                current_game_code = game_code
            elif choice == '2' and current_game_code is None:
                game_code = input("Vnesite kodo igre za pridružitev: ")
                send_message("#JOIN", client, game_code)
                current_game_code = game_code
            elif choice == '3':
                if current_game_code is not None:
                    message = input("Vnesite sporočilo: ")
                    send_message("#M", client, f"{current_game_code}:{message}")
                else:
                    print("Niste povezani z nobeno igro.")
            elif choice == '4':
                if current_game_code is not None:
                    send_message("#EXIT", client, current_game_code)
                    current_game_code = None
                else:
                    print("Niste povezani z nobeno igro.")
            elif choice.lower() == 'exit':
                break
            else:
                print("Neveljavna izbira.")
    except Exception as e:
        print("Napaka pri komunikaciji s strežnikom:", e)
    finally:
        client.close()

def send_message(protocol, client, message):
    try:
        message = protocol_encode(protocol, message)  # Dodajanje protokola
        encrypted_message = cipher_suite.encrypt(message.encode('utf-8'))
        client.sendall(encrypted_message)  # Pošiljanje šifriranega sporočila strežniku
    except Exception as e:
        print("Napaka pri pošiljanju podatkov:", e)

def listen_to_server(client):
    while True:
        try:
            encrypted_message = client.recv(BUFFER)  # Prejemanje šifriranega sporočila od strežnika
            if encrypted_message:
                message = cipher_suite.decrypt(encrypted_message).decode('utf-8')
                protocol, content = protocol_decode(message)
                response = protocol_check(protocol, content)
                if response != -1:
                    print(f"Sporočilo od strežnika: {response}")
            if not encrypted_message:
                break
        except ConnectionResetError:
            print("Povezava s strežnikom je bila prekinjena.")
            break
        except Exception as e:
            print("Napaka pri prejemanju podatkov:", e)
            break

def protocol_check(protocol, message):
    if protocol in ["#M", "#INFO", "#ERROR"]:
        return message
    else:
        return -1

def protocol_encode(protocol, message):
    return f"{protocol}/|/{message}"

def protocol_decode(message):
    try:
        str = message.split("/|/", 1)
        return (str[0], str[1])
    except Exception as e:
        print("Napaka pri dekodiranju sporočila:", e)
        return (None, None)

if __name__ == "__main__":
    main()
