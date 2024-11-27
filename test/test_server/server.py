import socket
import threading
from cryptography.fernet import Fernet

HOST = '127.0.0.1'
PORT = 1234  # Vrata strežnika
BUFFER_SIZE = 1024
running = True  # če je true potem strežnik posluša, sicer se konča

# Ključ za simetrično kriptiranje
key = "B8DRpjfj4ieG6zHMs7Ydn8O02MH8ZKnIMLCRoqvxFwA="
cipher_suite = Fernet(key)  # Ustvarjanje objekta za šifriranje in dešifriranje

s = None  # Globalno definiranje socketa

def main():
    global s  # Dovoljenje za spreminjanje globalnega socketa
    threading.Thread(target=wait_exit, args=(), daemon=True).start()
    connections = []
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
                connections.append(conn)
                threading.Thread(target=handle_client, args=(conn, addr, connections), daemon=True).start()
            except OSError:
                # Da ne pride do težav pri zapiranju strežnika z exit
                break
            except Exception as e:
                print(f"Napaka pri sprejemanju povezave: {e}")

    # Dodano: Zapiranje vseh povezav
    for conn in connections:
        conn.close()
    print("Strežnik je ugasnjen.")

def handle_client(conn, addr, connections):
    try:
        print(f"Povezan uporabnik: {addr}")
        while True:
            protocol, message = read_from_client(conn)
            if not message:
                break
            response = protocol_check(protocol, message)
            write_to_client("#M", conn, response)
    except Exception as e:
        print(f"Napaka pri obravnavi stranke {addr}: {e}")
    finally:
        conn.close()
        connections.remove(conn)
        print(f"Odjavljeni uporabnik: {addr}")

def read_from_client(client):
    try:
        encrypted_message = client.recv(BUFFER_SIZE)  # Prejemanje šifriranega sporočila od odjemalca
        if encrypted_message:
            decrypted_message = cipher_suite.decrypt(encrypted_message).decode('utf-8')
            #print(f"Prejeto šifrirano sporočilo: {encrypted_message}")
            print(f"Sporočilo: {decrypted_message}")
            return protocol_decode(decrypted_message)
    except Exception as e:
        print("Napaka pri branju sporočila od odjemalca:", e)
    return None

def write_to_client(protocol, client, message):
    try:
        message = protocol_encode(protocol, message)
        encrypted_response = cipher_suite.encrypt(message.encode('utf-8'))
        client.sendall(encrypted_response)  # Pošljite šifriran odgovor odjemalcu
        print(f"Odgovoril sem: {message}")
    except s.error as e:
        print("Napaka pri pošiljanju podatkov:", e)
    except UnicodeEncodeError as e:
        print("Napaka pri kodiranju podatkov:", e)

def wait_exit(): # Zaustavitev strežnika z ukazom 'exit'
    global running, s
    while True:
        message = input("Za izhod vnesite 'exit'! \n")
        if message.lower() == 'exit':
            print("Ugasnil sem strežnik.")
            running = False
            if s:
                s.close()  # Zapiranje socketa
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
    main()  # Zagon strežnika

