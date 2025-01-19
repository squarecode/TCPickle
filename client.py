import random
import socket
import pickle
from time import sleep

SERVER_ADDRESS = ("localhost", 50007)
MAGIC = "sauerkraut"

def check_send_another() -> bool:
    return True if (input("Send another block y/N?: ") == "y") else False


while True:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(SERVER_ADDRESS)
        data_to_tx = random.sample(range(1, 1000000000), 10000)
        serialized_data = pickle.dumps(data_to_tx)
        if check_send_another():
            sock.sendall(serialized_data)
            print("Data has been sent!")
        else:
            sock.sendall(pickle.dumps(MAGIC))
            break
    except socket.error as exc:
        if isinstance(exc, ConnectionRefusedError):
            print("Server inactive. Retrying in 1s ...")
            sleep(1)
        else:
            print()
    finally:
        sock.close()
