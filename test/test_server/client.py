import socket
from cryptography.fernet import Fernet

SERVER_IP = "147.185.221.23"  # IP naslov strežnika
PORT = 41818  # Vrata strežnika
BUFFER_SIZE = 1024  # Medpomnilnik za prejemanje podatkov

# Simetrično kriptiranje
key = "B8DRpjfj4ieG6zHMs7Ydn8O02MH8ZKnIMLCRoqvxFwA="

cipher_suite = Fernet(key)

def send_message(message):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP/IP vtičnica
        client.connect((SERVER_IP, PORT))  # Povezava s strežnikom
    
    except Exception as e:
        print("Napaka pri povezovanju s strežnikom:", e)
        return
    
    try:
        # Enkripcija sporočila s simetričnim ključem
        encrypted_message = cipher_suite.encrypt(message.encode('utf-8'))
        client.sendall(encrypted_message)  # Pošiljanje šifriranega sporočila strežniku
        encrypted_response = client.recv(BUFFER_SIZE)  # Prejemanje šifriranega sporočila od strežnika
        print(f"Prejeto šifrirano sporočilo: {encrypted_response}")
        response = cipher_suite.decrypt(encrypted_response).decode('utf-8')  # Dešifriranje sporočila
        print(f"Prejeto: {response}")
    except Exception as e:
        print("Napaka pri komunikaciji s strežnikom:", e)
    finally:
        client.close() 

if __name__ == "__main__":
    while True:
        message = input("Vnesite sporočilo za pošiljanje (ali 'exit' za izhod): ")
        if message.lower() == 'exit':
            break
        send_message(message)  # Pošiljanje sporočila strežniku
