import errno
import socket
import sys
import threading


def listen():
    try:
        while True:
            # Wait for query
            data, client_address = connection.receive_message()
            hostname = data.strip()

            # Check RR table for record
            record = rr_table.get_record(hostname)

            if record:
                # Record found
                response = f"{hostname},{record['type']},{record['result']},{record['ttl']},{record['static']}"
            else:
                # Record not found
                response = "Record not found"

            # Send response back to client
            connection.send_message(response, client_address)

            rr_table.display_table()
    except KeyboardInterrupt:
        print("Keyboard interrupt received, exiting...")
    finally:
        # Close UDP socket
        connection.close()


def main():
    # Add initial records for the authoritative Amazon server
    rr_table.add_record("shop.amazone.com", "A", "3.33.147.88", None, 1)
    rr_table.add_record("cloud.amazone.com", "A", "127.0.0.1", None, 1)

    # Bind address to UDP socket
    connection.bind(("127.0.0.1", 22000))

    listen()


class RRTable:
    def __init__(self):
        self.records = {}
        self.lock = threading.Lock()
        self.record_number = 0

    def add_record(self, name, record_type, result, ttl, static):
        with self.lock:
            self.record_number += 1
            self.records[name] = {
                "record_number": self.record_number,
                "name": name,
                "type": record_type,
                "result": result,
                "ttl": ttl,
                "static": static,
            }

    def get_record(self, name):
        with self.lock:
            return self.records.get(name)
        
    def display_table(self):
        with self.lock:
            print("record_number,name,type,result,ttl,static")
            for record in self.records.values():  # Iterate over the values, not the keys
                ttl_display = record['ttl'] if record['static'] == 0 else "None"
                print(f"{record['record_number']},{record['name']},{record['type']},{record['result']},{ttl_display},{record['static']}")



class UDPConnection:
    """A class to handle UDP socket communication, capable of acting as both a client and a server."""

    def __init__(self, timeout: int = 1):
        """Initializes the UDPConnection instance with a timeout. Defaults to 1."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)
        self.is_bound = False

    def send_message(self, message: str, address: tuple[str, int]):
        """Sends a message to the specified address."""
        self.socket.sendto(message.encode(), address)

    def receive_message(self):
        """
        Receives a message from the socket.

        Returns:
            tuple (data, address): The received message and the address it came from.

        Raises:
            KeyboardInterrupt: If the program is interrupted manually.
        """
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

    def bind(self, address: tuple):
        """Binds the socket to the given address. This means it will be a server."""
        if self.is_bound:
            print(f"Socket is already bound to address: {self.socket.getsockname()}")
            return
        self.socket.bind(address)
        self.is_bound = True

    def close(self):
        """Closes the UDP socket."""
        self.socket.close()


rr_table = RRTable()
connection = UDPConnection()

if __name__ == "__main__":
    main()
