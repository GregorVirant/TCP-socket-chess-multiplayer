import socket
import sys

SERVER_IP = "127.0.0.1"  # IP naslov strežnika
PORT = 1234  # Vrata strežnika
BUFFER_SIZE = 1024  # Medpomnilnik za prejemanje podatkov

def send_message(message):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP/IP vtičnica
        client.connect((SERVER_IP, PORT)) # Povezava s strežnikom
    
    except Exception as e:
        print("Napaka pri povezovanju s strežnikom:", e)
        return
    
    try:
        client.sendall(message.encode('utf-8'))  # Pošiljanje sporočila strežniku
        response = client.recv(BUFFER_SIZE).decode('utf-8')  # Prejemanje sporočila od strežnika
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
