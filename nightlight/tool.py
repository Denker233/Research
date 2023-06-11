import socket
def is_port_available(port):
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Set a timeout value (adjust as needed)
    sock.settimeout(1)
    
    try:
        # Attempt to connect to the port
        sock.connect(("localhost", port))
        # Port is not available
        return False
    except socket.error:
        # Port is available
        return True
    finally:
        # Close the socket
        sock.close()

def get_available_ports(start_port, end_port):
        available_ports = []
        for port in range(start_port, end_port + 1):
            if is_port_available(port):
                available_ports.append(port)
        return available_ports

def write_port_to_file(ports):
    with open("ports_websocket.txt", 'w') as file:
        for port in ports:
            file.write(str(port) + '\n')

def read_port_from_file():
    port_numbers = []
    with open("ports_websocket.txt", 'r') as file:
        for line in file:
            port_numbers.append(int(line.strip()))
    return port_numbers

def weighted_score(cpu_usage,memory_usage,network_latency):
    return float(cpu_usage) + float(memory_usage) + float(network_latency)

def weighted_round_robin(clients, weights):
    while True:
        client = random.choices(clients, weights=weights)[0]
        yield client