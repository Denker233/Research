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
def login(host_IP):
    url = 'http://'+host_IP+'/api/auth/login'

    headers = {"accept": "*/*", "Content-Type": "application/json"}

    data = {"username": username, "password": password}

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200 or response.status_code == 201:
        content = response.json()
        access_token = content.get("access_token")
        token_type = content.get("token_type")
        # print(token_type, " ", access_token)
        result = token_type+" "+access_token
        return result
    else:
        print("Error: Failed to retrieve Meross device status. Status code: {}".format(response.status_code))
        return

def find_device_load_info(host_IP):
    url = 'http://'+host_IP+'/api/accessories'

    authorization_code = login(host_IP)
    headers = {"accept": "*/*", "Authorization": authorization_code}

    response = requests.get(url, headers=headers)

    if response.status_code == 200 or response.status_code == 201:
        # print(response.json())
        data = response.json()
        filename = "hub_data.json"
        with open(filename, "w") as file:
            json.dump(data, file)
        devices = json.loads(data)  # Parse the JSON text into a list of dictionaries

        device_names = [device['serviceName'] for device in devices[1:]]
        return device_names
        # for item in data:
        #     # print(item)
        #     if item.get("serviceName") == device_name:
        #         # print(item.get("uniqueId"))
        #         # TODO: return the uniqueId of the device
        #         return item.get("uniqueId")
    else:
        print("Error: Failed to retrieve Meross device status. Status code: {}".format(response.status_code))
        return
