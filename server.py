import argparse
import socket
import hashlib

def read_keys(key_file):
    try:
        with open(key_file) as file:
            keys = [line.strip() for line in file.readlines()]
            return keys
    except FileNotFoundError:
        print("File not found")
        return[]
 
def main(port, key_file):

    keys = read_keys(key_file)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', port))
    sock.listen(1)
    
    while True:
        conn, addr = sock.accept()
        try:
            data = conn.recv(1024).decode('utf-8').strip()

            if data != "HELLO":
                print("Invalid message. Closing server")
                conn.close
                break

            while True:
                data = conn.recv(1024).decode('utf-8').strip()
                if not data:
                    break

                if data == "DATA":

                    sha256_hash = hashlib.sha256()

                    while True:
                        line = conn.recv(1024).decode('utf-8').strip()
                        if(line == "."):
                            break

                        sha256_hash.update(line.encode('utf-8'))

                    for key in keys:
                        sha256_hash.update(key.encode('utf-8'))

                    conn.sendall(b'270 SIG\n')
                    conn.sendall(sha256_hash.hexdigest().encode('utf-8') + b'\n')

                    response = conn.recv(1024).decode('utf-8').strip()

                    if response not in ["PASS", "FAIL"]:
                        print("Invalid message. Closing the connection.")
                        conn.close()
                        break

                elif data == "QUIT":
                    print("closed")
                    conn.close()
                    break

                else:
                    print("Received a default command:", data)
                    conn.close()
                    break

        finally:
            conn.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("listen_port", type = int, help = "Port to listen on")
    parser.add_argument("key_file", type = str, help = "Key file")

    args = parser.parse_args()

    main(args.listen_port, args.key_file)
