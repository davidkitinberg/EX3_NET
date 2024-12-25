import socket
import time
import threading

# Constants for server
HOST = '127.0.0.1'  # Localhost
PORT = 65432

# Server implementation
def server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print("Server is listening on port", PORT)

        conn, addr = server_socket.accept()
        with conn:
            print("Connected by", addr)

            # Handle maximum message size request
            data = conn.recv(1024).decode('utf-8')
            if data.startswith("REQUEST_MAX_SIZE"):
                max_size = 20  # Example max size
                conn.sendall(str(max_size).encode('utf-8'))

            received_messages = {}
            highest_ack = -1

            while True:
                data = conn.recv(1024).decode('utf-8')
                if not data:
                    break

                seq_num, message = data.split("|", 1)
                seq_num = int(seq_num)

                if seq_num == highest_ack + 1:
                    highest_ack = seq_num
                    received_messages[seq_num] = message

                    while highest_ack + 1 in received_messages:
                        highest_ack += 1

                else:
                    received_messages[seq_num] = message

                conn.sendall(f"ACK{highest_ack}".encode('utf-8'))