# Client implementation
import socket
import time
import threading


def client(message, max_size, window_size, timeout):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))

        # Request maximum message size
        client_socket.sendall("REQUEST_MAX_SIZE".encode('utf-8'))
        max_size = int(client_socket.recv(1024).decode('utf-8'))
        print("Max message size from server:", max_size)

        # Prepare messages
        chunks = [message[i:i+max_size] for i in range(0, len(message), max_size)]
        num_chunks = len(chunks)
        sent_acks = [-1] * num_chunks

        base = 0

        while base < num_chunks:
            for i in range(base, min(base + window_size, num_chunks)):
                if sent_acks[i] == -1:
                    client_socket.sendall(f"{i}|{chunks[i]}".encode('utf-8'))

            client_socket.settimeout(timeout)
            try:
                ack = client_socket.recv(1024).decode('utf-8')
                ack_num = int(ack[3:])

                for j in range(base, ack_num + 1):
                    sent_acks[j] = 1

                base = ack_num + 1

            except socket.timeout:
                print("Timeout! Resending from base index:", base)

if __name__ == "__main__":
    user_message = "This is a test message that will be split into smaller chunks"
    user_max_size = 20
    user_window_size = 4
    user_timeout = 5

    server_thread = threading.Thread(target=Server)
    server_thread.start()

    time.sleep(1)  # Allow server to start

    client(user_message, user_max_size, user_window_size, user_timeout)

    server_thread.join()