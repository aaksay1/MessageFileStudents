import socket
import sys

def main():
    server_name = sys.argv[1]
    server_port = int(sys.argv[2])
    message_filename = sys.argv[3]
    signature_filename = sys.argv[4]

    messages = []
    signatures = []

    # Open the message file and read messages
    with open(message_filename, 'r') as f:
        while True:
            length = f.readline().strip()
            if not length:
                break
            message = f.read(int(length)).strip()
            messages.append(message)

    # Open the signature file and read signatures
    with open(signature_filename, 'r') as f:
        for line in f:
            signatures.append(line.strip())

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_name, server_port))

        # Send HELLO message
        s.sendall(b"HELLO\n")
        response = recv_line(s)
        print(response)
        if response != "260 OK":
            print("Error: Unexpected server response")
            return

        # For each message in the messages array
        for index, message in enumerate(messages):
            s.sendall(b"DATA\n")
            s.sendall(message.encode() + b"\n.\n")
            
            response = recv_line(s)
            print(response)
            if response != "270 SIG":
                print("Error: Unexpected server response")
                return

            server_signature = recv_line(s)
            print(server_signature)

            if server_signature == signatures[index]:
                s.sendall(b"PASS\n")
            else:
                s.sendall(b"FAIL\n")

            response = recv_line(s)
            print(response)
            if response != "260 OK":
                print("Error: Unexpected server response")
                return

        # Send QUIT message
 
        s.sendall(b"QUIT\n")

def recv_line(sock, delimiter=b'\n'):
    """Receive data from the socket until a delimiter is found."""
    buffer = bytearray()
    while True:
        chunk = sock.recv(1)  # receive byte by byte
        if not chunk:
            # Connection closed
            break
        buffer.extend(chunk)
        if buffer.endswith(delimiter):
            break
    return buffer.decode().strip()

if __name__ == "__main__":
    main()