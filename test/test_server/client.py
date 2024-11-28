import socket
import threading
from cryptography.fernet import Fernet

 # Vrata strežnika
SERVER_IP = "127.0.0.1"  # IP naslov strežnika
PORT = 1234  # Vrata strežnika
BUFFER = 1024  # Medpomnilnik za prejemanje podatkov

# Ključ za simetrično kriptiranje
key = "B8DRpjfj4ieG6zHMs7Ydn8O02MH8ZKnIMLCRoqvxFwA="
cipher_suite = Fernet(key)

def main():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP/IP vtičnica
        client.connect((SERVER_IP, PORT))  # Povezava s strežnikom
    except Exception as e:
        print("Napaka pri povezovanju s strežnikom:", e)
        return
    threading.Thread(target=listen_to_server, args=(client,), daemon=True).start()

    try:
        while True:
            message = input("Vnesite sporočilo za pošiljanje (ali 'exit' za izhod): ")
            if message.lower() == 'exit':
                break
            send_message("#M", client, message)
    except Exception as e:
        print("Napaka pri komunikaciji s strežnikom:", e)
    finally:
        client.close()

def send_message(protocol, client, message):
    try:
        message = protocol_encode(protocol, message) # Dodajanje protokola
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
                protocol, message = protocol_decode(message)
                message = protocol_check(protocol, message)
                print(f"Sporočilo od strežnika: {message}")
            if not encrypted_message:
                break
        except ConnectionResetError:
            print("Povezava s strežnikom je bila prekinjena.")
            break
        except Exception as e:
            print(f"Napaka pri prejemanju podatkov: {e}")
            break

def protocol_check(protocol, message):
    if protocol == "#M":
        return message
    else:
        return -1
    
def protocol_encode(protocol, message):
    return f"{protocol}/|/{message}"

def protocol_decode(message):
    try:
        str = message.split("/|/")
    except Exception as e:
        print("Napaka pri dekodiranju sporočila", e)
        return None, None
    return (str[0], str[1])

if __name__ == "__main__":
    main()
