import random
import socket
import pickle

SERVER_ADDRESS = ('localhost', 50007)
MAGIC = "sauerkraut"
CHUNK_SIZE = 4096

def collect_some_data(sock):
    print("Waiting for a client to connect and send data ...")
    client, addr = sock.accept()

    try:
        print(f"New Connection by: {addr}")
        data = b''
        chunks = []
        while True:
            chunk = client.recv(CHUNK_SIZE)
            if not chunk:
                break
            chunks.append(chunk)
        data += b''.join(chunks)
        rxed_obj = pickle.loads(data)
        print(f"Rxed: {len(rxed_obj)} values")
    finally:
        client.close()
        return rxed_obj

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(SERVER_ADDRESS)
    sock.listen(1)

    while True:
        data = collect_some_data(sock)
        if isinstance(data, str):
            if data == MAGIC:
                print("Got the magic! Shutting down")
                break
    sock.close()
            
