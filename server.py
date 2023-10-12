import socket
import sys
import hashlib

def main():
    listen_port = int(sys.argv[1])
    key_file = sys.argv[2]

    with open(key_file, 'r') as f:
        keys = [line.strip() for line in f.readlines()]

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', listen_port))
        s.listen()

        conn, addr = s.accept()
        with conn:
            data = conn.recv(1024).decode().strip()
            print(data)
            if data != "HELLO":
                print("Error: Unexpected client request")
                conn.close()
                return
            conn.sendall(b"260 OK\n")

            while True:
                command = conn.recv(1024).decode().strip()
                print(command)

                if command == "DATA":
                    message_lines = []
                    hash_obj = hashlib.sha256()
                    while True:
                        line = conn.recv(1024).decode().strip()
                        print(line)
                        if line == ".":
 
                            break
                        hash_obj.update(line.encode())
                        message_lines.append(line)

                    hash_obj.update(keys[len(message_lines) % len(keys)].encode())
                    signature = hash_obj.hexdigest()

                    conn.sendall(b"270 SIG\n")
                    conn.sendall(signature.encode() + b"\n")

                    response = conn.recv(1024).decode().strip()
                    print(response)
                    if response not in ["PASS", "FAIL"]:
                        print("Error: Unexpected client response")
                        conn.close()
                        return
                    conn.sendall(b"260 OK\n")

                elif command == "QUIT":
                    conn.close()
                    return

                else:
                    print("Error: Unknown command")
                    conn.close()
                    return

if __name__ == "__main__":
    main()