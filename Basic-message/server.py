import socket
import hashlib
import sys

def main():
    listen_port = int(sys.argv[1])
    key_file = sys.argv[2]

    keys = []

    with open(key_file, 'r') as f:
        for line in f:
            keys.append(line.strip())

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', listen_port))
    s.listen(1)

    while True:
        conn, addr = s.accept()

        data = conn.recv(1024).decode('ascii')
        print(data)  # Print received HELLO message

        if data != "HELLO":
            conn.close()
            continue

        conn.sendall("260 OK".encode('ascii'))

        while True:
            data = conn.recv(1024).decode('ascii')

            if data == "DATA":
                hasher = hashlib.sha256()
                message = ""
                while True:
                    line = conn.recv(1024).decode('ascii')
                    print(line)  # Print received message lines

                    if line.endswith("\\n."):
                        message += line[:-3]
                        break
                    message += line

                hasher.update((message + keys[0]).encode('ascii'))

                signature = hasher.hexdigest()
                conn.sendall("270 SIG".encode('ascii'))
                conn.sendall(signature.encode('ascii'))

                response = conn.recv(1024).decode('ascii')

                if response not in ["PASS", "FAIL"]:
                    conn.close()
                    break

                conn.sendall("260 OK".encode('ascii'))

            elif data == "QUIT":
                print(data)  # Print received QUIT message
                conn.close()
                sys.exit(0)  # Terminate the server

if __name__ == "__main__":
    main()
