import socket
import time
import threading
from Client import DEFAULT_SERVER_PORT, DEFAULT_SERVER_HOST

# Constants for server
HOST = DEFAULT_SERVER_HOST  # Localhost
PORT = DEFAULT_SERVER_PORT
MAX_SIZE = 1024
import socket
from threading import Thread

class Server:
    def __init__(self, host: str, port: int, max_size: int):
        self.host = host
        self.port = port
        self.max_size = max_size  # Maximum size of a single message chunk
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []  # To keep track of active connections

    def start(self):
        """
        Starts the server and listens for incoming client connections.
        """
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)  # Listen for up to 5 connections
        print(f"Server listening on {self.host}:{self.port}")

        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                print(f"Connection established with {client_address}")
                # Handle each client in a separate thread
                client_thread = Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.start()
                self.connections.append(client_socket)
        except KeyboardInterrupt:
            print("Server shutting down...")
            self.shutdown()

    def handle_client(self, client_socket: socket.socket, client_address: tuple):
        """
        Handles communication with a single client.
        """
        try:
            # Step 1: Receive request from client
            request = client_socket.recv(1024).decode('utf-8')
            print(f"Received request from {client_address}:\n{request}")

            # Step 2: Check for REQUEST_MAX_SIZE and respond
            if "REQUEST_MAX_SIZE" in request:
                client_socket.sendall(str(self.max_size).encode('utf-8'))
                print(f"Sent max size {self.max_size} to {client_address}")

            # Step 3: Receive message chunks
            received_chunks = {}
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break

                # Extract chunk ID and content
                if ":" in data:
                    chunk_id, content = data.split(":", 1)
                    chunk_id = int(chunk_id[1:])  # Extract chunk number (e.g., M0 -> 0)
                    received_chunks[chunk_id] = content
                    print(f"Received chunk M{chunk_id} from {client_address}")

                    # Send acknowledgment
                    ack_message = f"ACK{chunk_id}"
                    client_socket.sendall(ack_message.encode('utf-8'))
                    print(f"Sent {ack_message} to {client_address}")

        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
        finally:
            client_socket.close()
            print(f"Connection closed with {client_address}")

    def shutdown(self):
        """
        Shuts down the server and closes all connections.
        """
        for conn in self.connections:
            conn.close()
        self.server_socket.close()

if __name__ == "__main__":
    import argparse

    # Argument parser for server configuration
    arg_parser = argparse.ArgumentParser(description="A Sliding Window Server.")
    arg_parser.add_argument("-p", "--port", type=int, default=DEFAULT_SERVER_PORT, help="Port to listen on.")
    arg_parser.add_argument("-H", "--host", type=str, default=DEFAULT_SERVER_HOST, help="Host to bind to.")
    arg_parser.add_argument("-s", "--max-size", type=int, default=20, help="Maximum chunk size.")

    args = arg_parser.parse_args()

    # Start the server
    server = Server(host=args.host, port=args.port, max_size=args.max_size)
    server.start()

# # Server implementation
# def server():
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
#         server_socket.bind((HOST, PORT))
#         server_socket.listen()
#         print("Server is listening on port", PORT)
#
#         conn, addr = server_socket.accept()
#         with conn:
#             print("Server connected by", addr)
#
#             # Handle maximum message size request
#             data = conn.recv(1024).decode('utf-8')
#             if data.startswith("REQUEST_MAX_SIZE"):
#                 max_size = MAX_SIZE
#                 conn.sendall(str(max_size).encode('utf-8'))
#
#             received_messages = {}
#             highest_ack = -1
#
#             while True:
#                 data = conn.recv(1024).decode('utf-8')
#                 if not data:
#                     print('Server did not receive any data')
#                     break
#
#                 seq_num, message = data.split("|", 1)
#                 seq_num = int(seq_num)
#
#                 if seq_num == highest_ack + 1:
#                     highest_ack = seq_num
#                     received_messages[seq_num] = message
#
#                     while highest_ack + 1 in received_messages:
#                         highest_ack += 1
#
#                 else:
#                     received_messages[seq_num] = message
#
#                 conn.sendall(f"ACK{highest_ack}".encode('utf-8'))