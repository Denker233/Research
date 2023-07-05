import boto3
import os
import requests
from botocore.handlers import disable_signing
import asyncio
import websockets
from botocore.exceptions import ClientError
import logging
from azure.storage.blob import BlobServiceClient
from flask import Flask, request
import time
import threading
import subprocess
import tool
import psutil
import sys
import socket
from urllib.request import urlopen



system_name = ""
loop=0
running_modules = [] #for each node
connected_clients = set() #for leader node
client_map = [] #for leader node
module_to_assign_map=[] #wait to be assigned to other nodes
cached_modules=[] # list of cached modules for each node;a remove element from list need to be implemented to make space for popular ones
devices=[]


app = Flask(__name__)
# @app.route('/post', methods=['POST'])
class Kern:
    def __init__(self):
        self.leader=0
        self.loop=0
        self.download=0
        self.credential=None
        self.leader_ip=None
        self.ID=None

    def query_device(self):
        f_name="hub_urls.txt"
        hub_urls = []
        with open(f_name, "r") as file:
            for line in file:
                url = line.strip()  # Remove leading/trailing whitespace
                hub_urls.append(url)
        for url in hub_urls:
            devices.append(tool.find_device_load_info(url))
    def boot(self):
        url = "https://dcsg-diot-frontend.vercel.app/api/status"
        hostname = socket.gethostname()
        print("My host name is "+hostname)
        try:
            ip_address = socket.gethostbyname_ex(hostname)
        except socket.gaierror as e:
            print("Error: ", e)
            ip_address = None
        print("My IP address is "+str(ip_address))
        ip = urlopen('http://ip.42.pl/raw').read().decode()
        print('本机所在公网IP是: ', ip)
        self.query_device()
        print("devices are "+devices)
        data = {"type":"boot", "name": system_name,"IP":'134.84.0.1',"devices":devices}
        response = requests.post(url, data=data)
        response = response.json()
        print(response)
        #change leader_ip into internet IP

        # self.leader_ip="223.81.148.1"
        # self.leader_ip='134.84.0.1'
        self.leader_ip='10.20.41.157'
        # self.leader_ip = response['system']["IP"]
        # self.ID = response['system']["id"]
        # print(response)

    # def follower_boot(self):
    #     url = "https://dcsg-diot-frontend.vercel.app/api/status"
    #     data = {"type":"boot", "name": system_name}
    #     response = requests.post(url, data=data)
    #     response = response.json()
    #     self.credential = response["credential"]
    #     self.leader_ip = response["IP"]
    #     print(response)
    
    def balancing_decision_run(self,f,content,module_id):
        leadder_cpu = psutil.cpu_percent(interval=1)
        leader_memory =psutil.virtual_memory().percent
        leader_network=0.0
        #update leader_node once make a decision
        for client in client_map:
            if client["websocket"]==-1:
                client['cpu_usage'] = leadder_cpu
                client['memory_usage'] = leader_memory
                client['network_latency'] = leader_network
                client["score"] = tool.weighted_score(leadder_cpu,leader_memory,leader_network)
                client["running_modules"] = running_modules
                client['cached_modules'] = cached_modules
        sorted_client_map = sorted(client_map, key=lambda x: x['score'])
        chosed_websocket = sorted_client_map[0]["websocket"]
        # #use weighted round roubin to get the specific node to assign module
        # weights = [1 / (client["cpu_usage"] * client["memory_usage"] * client["network_latency"]) for client in client_map]
        # # Normalize the weights
        # total_weight = sum(weights)
        # weights = [weight / total_weight for weight in weights]
        # algorithm = tool.weighted_round_robin(client_map,weights)["websocket"]
        # chosed_websocket = next(algorithm)
        if chosed_websocket == -1: # run at the leader node
            subprocess.run(["python3", f.name])
            print("module:{} running at the leader node".format(f.name))
        else: #add to the ready to assign map and assign them at the next heartbeat cycle
            #need to time it if it doesn't send to the specific node and try the next best node
            module_to_assign_map.append({
                'websocket':chosed_websocket,
                'module_id':module_id,
                'module_name': f.name.split(".")[0], 
                'content' : content})#the second parameter stands for module name
            print("module to assign to follower node")

    def heartbeat_server(self):
        while True:
            print("in heart beat server")
            time.sleep(1)
            url = "https://dcsg-diot-frontend.vercel.app/api/status"
            data = {"type":"beat", "ID":self.ID,"name": system_name,"IP":'134.84.0.1'}
            response = requests.post(url, data=data)
            response = response.json()
            modules = response["system"]["modules"]
            for module in modules:
                if module['id'] not in cached_modules:
                    print("module['id'] is "+module['id'])
                    print("module['filename'] is "+module['filename'])
                    download_response = requests.get("https://dcsg-diot-frontend.vercel.app/api/fetchModule/{}".format(module['id']))
                    if download_response.status_code == 200:
                        with open(module['filename'], "wb") as f:
                            f.write(download_response.content)
                            cached_modules.append(module['id'])
                        print(f.name)
                        self.balancing_decision_run(f,download_response.content,module['id'])
                    else:
                        print("Error downloading file.")
                else: #in cache then run it directly
                    with open(module['filename'], "r") as f:
                        content= f.read()
                        self.balancing_decision_run(f,content,module['id'])   

            
            # pong = response["result"]
            # module_name = response["module_name"]
            # if module_name not in cached_modules:
            #     download_response = requests.get(response["url"])
            #     if download_response.status_code == 200:
            #         with open(module_name+".py", "wb") as f:
            #             f.write(download_response.content)
            #             cached_modules.append(module_name)
            #         print(f.name)
            #         self.balancing_decision_run(f,download_response.contentmodule['id'])
            #     else:
            #         print("Error downloading or executing file.")
            # else: #in cache then run it directly
            #     with open(module_name+".py", "r") as f:
            #         content= f.read()
            #         self.balancing_decision_run(f,contentmodule['id'])   
            print(response)

    async def node_heartbeat(self,port):#follower send
        # url = "ws://localhost:{}".format(port)
        url = f"ws://{self.leader_ip}:8765/websocket"
        print("url is "+url)
        while True:
            time.sleep(3)
            async with websockets.connect(url,ping_interval=None) as websocket:
                cpu_usage = psutil.cpu_percent(interval=1)
                memory_usage = psutil.virtual_memory().percent
                await websocket.send("ping: {}; cpu usage: {}; memory_usage: {};cached_modules: {};running_modules: {};ID: {}".format(port,cpu_usage,memory_usage,cached_modules,running_modules,self.ID)) 
                result = await websocket.recv()
                print("first result")
                print(result)
                if result.split(":")[0]=="pong":
                    print("receive pong: ")
                elif result.split(":")[0]=="cache":
                    module_id = result.split(":")[1]
                    module_name = result.split(":")[2]
                    with open(module_name+".py", "r+") as f:
                        result = subprocess.run(["python3", f.name], capture_output=True, text=True)
                        print("cached module running at follower node")
                    print("second result")
                    print(result)
                else:#recv a module:content download and run i
                    print("in else statement")
                    module_id = result.split(":")[0]
                    module_name = result.split(":")[1]
                    module_content = result.split(":")[2]
                    with open(module_name+".py", "r+") as f:
                        f.write(module_content)
                        f.seek(0)
                        cached_modules.append(module_id)
                        try:
                            print("in try")
                            print(f.name)
                            result = subprocess.run(["python3", f.name], capture_output=True, text=True)
                            if result.returncode == 0:
                                print("Command executed successfully!")
                                print("Output:", result.stdout)
                            else:
                                print("Command execution failed!")
                                print("Error:", result.stderr)
                        except subprocess.CalledProcessError as e:
                            print("Command execution failed with exception!")
                            print("Exception:", e)
                    print("module running at follower node")
                    running_modules.append(module_id)
    
    async def handle_connection(self,websocket, path): #leader get data from follower
        # Add the client to the set of connected clients
        connected_clients.add(websocket)
        print("websocket:{}".format(websocket))
        client_id = id(websocket)
        client_map.append ({
            'websocket': websocket,
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'network_latency': 0.0,
            'score': sys.float_info.max,
            'running_modules' :[],
            'cached_modules' : [],
            "node_ID":None
            })

        try:
            while True:

                for item in module_to_assign_map:
                    # if websocket matches then send the module content to the client
                    # print("websocket from the module_map:{} and websocket of")
                    for client in client_map:
                        # print("websocket from the module_map:{} and websocket of client_map{}".format(item['websocket'],client['websocket']))
                        if item['websocket'] == client['websocket']:
                            if item['module_id'] not in client['cached_modules']:
                                print("in sending module to follower")
                                response = item['module_id']+":"+item["module_name"]+":"+item["content"] #module_id:module_name:content
                                await websocket.send(response)
                                print("module send to the follower")
                            else:#it is alreadly cached
                                response = "cache"+":"+item['module_id']+":"+item["module_name"]
                                await websocket.send(response)
                                print("send that is already in cache")
                            module_to_assign_map.remove(item) #remove the module sent from the list
                # Receive message from the client
                start_time = time.time()
                message = await websocket.recv()
                end_time = time.time()
                print(f"Received message: {message}")
                network_latency = end_time - start_time

                components=message.split(';')
                if len(components)>=1:#ping
                    ping=components[0].split(":")[1]
                    cpu_usage=components[1].split(":")[1]
                    memory_usage=components[2].split(":")[1]
                    cached_modules_from_node = components[3].split(":")[1]
                    print("cached_module: "+cached_modules_from_node)
                    running_modules_from_node = components[4].split(":")[1]
                    print("running modules: "+running_modules_from_node)
                    ID = components[5].split(":")[1]
                    print(ping)
                    response="pong:"
                    for item in client_map: #there must be a dummy item in the dic
                        if item['websocket'] ==websocket: # find the correspending websocket/node
                            item['cpu_usage'] = cpu_usage
                            item['memory_usage'] = memory_usage
                            item['network_latency'] = network_latency
                            item['score'] = tool.weighted_score(cpu_usage,memory_usage,network_latency)
                            item['cached_modules'] = cached_modules_from_node
                            item['running_modules'] = running_modules_from_node
                            item["node_ID"] = ID
                    print("network latency: {}".format(network_latency))
                else:
                    response="wrong"
                expiration=500
                await websocket.send(response)

                
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            # Remove the client from the set of connected clients
            connected_clients.remove(websocket)

# Start the WebSocket server
    async def start_server(self):
        #use your internet IP
        async with websockets.serve(self.handle_connection, "10.20.41.157", 8765):
            await asyncio.Future()  # Run forever
    

k1=Kern()
system_name = input("System Name?")
k1.boot()
# k1.ID="cljgic52m0000qfdoq0m6i0rp"
decision = input("Leader?")
ports_websocket = []
if decision=="leader":
    print("in leader")
    k1.leader=1
    leadder_cpu = psutil.cpu_percent(interval=1)
    leader_memory =psutil.virtual_memory().percent
    leader_network=0.0
    leader_node = {
            'websocket': -1,
            'cpu_usage':  100,
            'memory_usage': 100,
            'network_latency': leader_network,
            'score': tool.weighted_score(leadder_cpu,leader_memory,leader_network),
            'running_modules' : running_modules,
            'cached_modules' : cached_modules
        }
    client_map.append(leader_node)
    node_max_num=int(input("How many nodes do you want to handle at most?"))
    module_to_assign_map= [] * node_max_num
    ports_websocket = tool.get_available_ports(6000,6000+int(node_max_num))# test for 10 ports reserved for websocket
    tool.write_port_to_file(ports_websocket)
    leader_heartbeat_server = threading.Thread(target=k1.heartbeat_server)# heartbeat frontend server
    leader_heartbeat_server.start()
    # print("after leader_heartbeat_server.start")
    # leader_heartbeat_threads = []
    # for i in range(0,node_max_num):
    #     print(f"i:{i} and port number at the leader side: {ports_websocket[i]}")
    #     loop = k1.create_event_loop()
    #     leader_heartbeat_thread = threading.Thread(target=k1.run_connect_follower_heart(str(ports_websocket[i]),loop))
    #     # leader_heartbeat_thread = threading.Thread(target=asyncio.run(k1.connect_follower_heart(str(ports_websocket[i]))))# must run after heartbeat server
    #     leader_heartbeat_thread.start()
    #     leader_heartbeat_threads.append(leader_heartbeat_thread)
    #     print("creat each thread{i}")
    # print("after leader beat")
    
    # leader_heartbeat_tasks = []

    # for i in range(0, node_max_num):
    #     print(f"i: {i} and port number at the leader side: {ports_websocket[i]}")
    #     task = asyncio.create_task(k1.connect_follower_heart(str(ports_websocket[i])))
    #     leader_heartbeat_tasks.append(task)
    #     print(f"created task {i}")

    # # Run the event loop to execute all tasks
    # asyncio.run(asyncio.wait(leader_heartbeat_tasks))
    
    asyncio.run(k1.start_server())
else:
    ports_websocket = tool.read_port_from_file()
    if ports_websocket == []:
        print("You should run leader first!!")
        sys.exit(0)
    # port_index = int(input("port index?"))
    # print(f"port number at the follower side: {ports_websocket[port_index]}")
    # follower_thread = threading.Thread(target=asyncio.run(k1.node_heartbeat(ports_websocket[port_index])))
    follower_thread = threading.Thread(target=asyncio.run(k1.node_heartbeat("8765")))
    follower_thread.start()
print("after if and else")
# k1.heartbeat_server()
while True:
    print("in while loop")
    k1.loop=k1.loop+1
for thread in leader_heartbeat_threads:
        thread.join()
if k1.leader==0:
    follower_thread.join()
else:
    leader_heartbeat_server.join()

