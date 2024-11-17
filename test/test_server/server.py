import socket
from datetime import datetime
import os

PORT = 1234  # Vrata strežnika
BUFFER_SIZE = 1024  # Konstantna velikost bufferja

def start_server():
    try:
        print("Strežnik:")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP/IP vtičnica
        server.bind(('0.0.0.0', PORT))  # Povezava vtičnice na naslov in vrata
        server.listen()  # Začnite poslušati povezave
        print(f"Poslušam na naslovu 127.0.0.1:{PORT}")
    except socket.error as e:
        print("Napaka pri zagonu strežnika:", e)
        return

    while True:
        try:
            client, address = server.accept()  # Sprejem povezave od odjemalca
            client_ip, client_port = address  # Pridobite IP naslov in vrata odjemalca
            print(f"Odjemalec se je povezal: {client_ip}:{client_port}")

            message = read_from_client(client)  # Pridoibte sporočilo od odjemalca
            if message:
                response = protocol(message)  # Obravnava protokola
                write_to_client(client, response)  # Pošiljanje odgovora odjemalcu
        except Exception as e:
            print("Prišlo je do napake:", e)
        finally:
            client.close()
            print(f"Odjemalec se je odklopil: {client_ip}:{client_port}\n")

def read_from_client(client):
    try:
        data = client.recv(BUFFER_SIZE)  # Prejem podatkov od odjemalca
        return data.decode('utf-8')  # UTF-8 dekodiranje podatkov
    except socket.error as e:
        print("Napaka pri prejemanju podatkov:", e)
        return None
    except UnicodeDecodeError as e:
        print("Napaka pri dekodiranju podatkov:", e)
        return None

def write_to_client(client, message):
    try:
        client.sendall(message.encode('utf-8'))  # Pošljite podatke odjemalcu
        print(f"Odgovoril sem: {message}")
    except socket.error as e:
        print("Napaka pri pošiljanju podatkov:", e)
    except UnicodeEncodeError as e:
        print("Napaka pri kodiranju podatkov:", e)

def protocol(message):
    return f"Prejeto sporočilo: {message}"

if __name__ == "__main__":
    start_server()  # Zagon strežnika

