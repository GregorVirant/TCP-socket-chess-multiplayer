import socket
from cryptography.fernet import Fernet

PORT = 1234  # Vrata strežnika
BUFFER_SIZE = 1024  # Konstantna velikost bufferja

# Simetrično kriptiranje
key = "B8DRpjfj4ieG6zHMs7Ydn8O02MH8ZKnIMLCRoqvxFwA="
cipher_suite = Fernet(key) # Ustvarjanje objekta za šifriranje in dešifriranje

def start_server():
    try:
        print("Strežnik:")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP/IP vtičnica
        server.bind(('0.0.0.0', PORT))  # Povezava vtičnice na naslov in vrata
        server.listen()  # Začnite poslušati povezave
        print(f"Poslušam na naslovu 0.0.0.0:{PORT}")
    except socket.error as e:
        print("Napaka pri zagonu strežnika:", e)
        return

    while True:
        try:
            client, address = server.accept()  # Sprejem povezave od odjemalca
            client_ip, client_port = address  # Pridobite IP naslov in vrata odjemalca
            print(f"Odjemalec se je povezal: {client_ip}:{client_port}")

            message = read_from_client(client)  # Pridobite sporočilo od odjemalca
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
        encrypted_message = client.recv(BUFFER_SIZE)  # Prejemanje šifriranega sporočila od odjemalca
        if encrypted_message:
            # Decrypt the message using the symmetric key
            decrypted_message = cipher_suite.decrypt(encrypted_message).decode('utf-8')
            print(f"Prejeto šifrirano sporočilo: {encrypted_message}")
            print(f"Dešifrirano sporočilo: {decrypted_message}")
            return decrypted_message
    except Exception as e:
        print("Napaka pri branju sporočila od odjemalca:", e)
    return None

def write_to_client(client, message):
    try:
        # Encrypt the response using the symmetric key
        encrypted_response = cipher_suite.encrypt(message.encode('utf-8'))
        client.sendall(encrypted_response)  # Pošljite šifriran odgovor odjemalcu
        print(f"Odgovoril sem: {message}")
    except socket.error as e:
        print("Napaka pri pošiljanju podatkov:", e)
    except UnicodeEncodeError as e:
        print("Napaka pri kodiranju podatkov:", e)

def protocol(message):
    return f"Prejeto sporočilo: {message}"

if __name__ == "__main__":
    start_server()  # Zagon strežnika

