import socket
import hashlib
import sys

def main():
    server_name = sys.argv[1]
    server_port = int(sys.argv[2])
    message_filename = sys.argv[3]
    signature_filename = sys.argv[4]
    
    messages = []
    signatures = []

    with open(message_filename, 'r') as f:
        while True:
            length = f.readline().strip()
            if not length:
                break
            message = f.read(int(length)).strip()
            messages.append(message)

    with open(signature_filename, 'r') as f:
        for line in f:
            signatures.append(line.strip())

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_name, server_port))

    s.sendall("HELLO".encode('ascii'))
    data = s.recv(1024).decode('ascii')
    print(data)

    if data != "260 OK":
        print("Error")
        sys.exit(1)

    for i, message in enumerate(messages):
        s.sendall("DATA".encode('ascii'))
        s.sendall((message + "\\n.").encode('ascii'))

        data = s.recv(1024).decode('ascii')
        print(data)

        if data != "270 SIG":
            print("Error")
            sys.exit(1)

        signature = s.recv(1024).decode('ascii')
        print(signature)

        if signature == signatures[i]:
            s.sendall("PASS".encode('ascii'))
        else:
            s.sendall("FAIL".encode('ascii'))

        data = s.recv(1024).decode('ascii')
        print(data)

        if data != "260 OK":
            print("Error")
            sys.exit(1)

    s.sendall("QUIT".encode('ascii'))
    s.close()

if __name__ == "__main__":
    main()
