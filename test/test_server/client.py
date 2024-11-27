import socket
from cryptography.fernet import Fernet

SERVER_IP = "127.0.0.1"  # IP naslov strežnika
PORT = 1234  # Vrata strežnika
BUFFER = 1024  # Medpomnilnik za prejemanje podatkov

# Simetrično kriptiranje
KEY = "B8DRpjfj4ieG6zHMs7Ydn8O02MH8ZKnIMLCRoqvxFwA="
cipher_suite = Fernet(KEY)

def main():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP/IP vtičnica
        client.connect((SERVER_IP, PORT))  # Povezava s strežnikom
    except Exception as e:
        print("Napaka pri povezovanju s strežnikom:", e)
        return
    try:
        while True:
            message = input("Vnesite sporočilo za pošiljanje (ali 'exit' za izhod): ")
            if message.lower() == 'exit':
                break
            send_message(client, message)
    except Exception as e:
        print("Napaka pri komunikaciji s strežnikom:", e)
    finally:
        client.close()

def send_message(client, message):
    try:
        # Enkripcija sporočila s simetričnim ključem
        encrypted_message = cipher_suite.encrypt(message.encode('utf-8'))
        client.sendall(encrypted_message)  # Pošiljanje šifriranega sporočila strežniku
        encrypted_response = client.recv(BUFFER)  # Prejemanje šifriranega sporočila od strežnika
        #print(f"Prejeto šifrirano sporočilo: {encrypted_response}")
        response = cipher_suite.decrypt(encrypted_response).decode('utf-8')  # Dešifriranje sporočila
        print(f"Prejeto: {response}")
    except Exception as e:
        print("Napaka pri pošiljanju ali prejemanju podatkov:", e)

if __name__ == "__main__":
    main()  # Zagon odjemalca
