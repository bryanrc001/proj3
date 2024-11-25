import errno
import socket
import sys
import threading


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
    def __init__(self, timeout: int = 1):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)
        self.is_bound = False

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

    def bind(self, address: tuple):
        if self.is_bound:
            print(f"Socket is already bound to address: {self.socket.getsockname()}")
            return
        self.socket.bind(address)
        self.is_bound = True

    def close(self):
        self.socket.close()


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
                # Record not found, forward to authoritative server
                connection.send_message(hostname, amazone_dns_address)
                response, _ = connection.receive_message()

            # Send response back to client
            connection.send_message(response, client_address)

            # Display RR table
            rr_table.display_table()
    except KeyboardInterrupt:
        print("Keyboard interrupt received, exiting...")
    finally:
        connection.close()


def main():
    # Add initial records for the local DNS server
    rr_table.add_record("www.csusm.edu", "A", "144.37.5.45", None, 1)
    rr_table.add_record("my.csusm.edu", "A", "144.37.5.150", None, 1)
    rr_table.add_record("amazone.com", "NS", "dns.amazone.com", None, 1)
    rr_table.add_record("dns.amazone.com", "A", "127.0.0.1", None, 1)

    # Bind address to UDP socket
    connection.bind(("127.0.0.1", 21000))

    listen()


rr_table = RRTable()
connection = UDPConnection()
amazone_dns_address = ("127.0.0.1", 22000)

if __name__ == "__main__":
    main()
