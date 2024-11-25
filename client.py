import errno
import socket
import sys


class UDPConnection:
    def __init__(self, timeout: int = 1):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)

    def send_message(self, message: str, address: tuple[str, int]):
        self.socket.sendto(message.encode(), address)

    def receive_message(self):
        while True:
            try:
                data, address = self.socket.recvfrom(4096)
                return data.decode(), address
            except socket.timeout:
                continue
            except OSError as e:
                if e.errno == errno.ECONNRESET:
                    print("Error: Unable to reach the other socket. It might not be up and running.")
                else:
                    print(f"Socket error: {e}")
                self.close()
                sys.exit(1)
            except KeyboardInterrupt:
                raise

    def close(self):
        self.socket.close()


def listen():
    try:
        while True:
            hostname = input("Enter hostname (or 'quit' to exit): ").strip()
            if hostname.lower() == "quit":
                break

            # Send query to local DNS server
            connection.send_message(hostname, local_dns_address)

            # Wait for response
            try:
                response, _ = connection.receive_message()
                print(f"Response: {response}")
            except Exception as e:
                print(f"Error receiving response: {e}")
    except KeyboardInterrupt:
        print("Keyboard interrupt received, exiting...")
    finally:
        connection.close()


def main():
    global local_dns_address
    local_dns_address = ("127.0.0.1", 21000)

    # Start listening for user input
    listen()


connection = UDPConnection()

if __name__ == "__main__":
    main()
