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



ID = "xxxx"
device_name="node1"
loop=0



app = Flask(__name__)
# @app.route('/post', methods=['POST'])
class Kern:
    def __init__(self):
        self.leader=0
        self.loop=0
        self.download=0

    def download_blob_to_file(self,blob_service_client: BlobServiceClient, container_name, bolb):
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=bolb)
        with open(file=os.path.join('/home/tian0138/csci-5105/Research', bolb), mode="wb") as sample_blob:
            download_stream = blob_client.download_blob()
            sample_blob.write(download_stream.readall())
            return sample_blob.name
    def handle_post_request(self,response):
        # Get the data from the request body
        print("in download")
        ID = response["ID"]
        container = response["container"]
        bolb = response["bolb"]
        account_name = response["account_name"]
        account_url = "https://{}.blob.core.windows.net".format(account_name)
        blob_service_client = BlobServiceClient(account_url=account_url)
        filepath=self.download_blob_to_file(blob_service_client,container,bolb)
        # Process the data...
        print("success")
        print(filepath)
        subprocess.run(["python", filepath])
        return 'Success'

    def boot(self):
        url = 'http://localhost:8001/post'
        data = {"type":"boot", "ID": ID, "device_name": device_name}
        response = requests.post(url, data=data)
        response = response.json()
        print(response)
        self.handle_post_request(response)
    
    def heartbeat_server(self):
        while True:
            print("in heart beat server")
            time.sleep(5)
            url = 'http://localhost:8001/post'
            data = {"type":"beat", "ID": ID, "device_name": device_name}
            response = requests.post(url, data=data)
            response = response.json()
            pong = response["result"]
            if self.download==0:
                download_response = requests.get(response["url"])
                # download_response = requests.get("https://dcsg-diot-frontend-kanishk-k.vercel.app/api/fetchModule/kanishk.py")
                if download_response.status_code == 200:
                    with open("minrui.py", "wb") as f:
                        f.write(download_response.content)
                    self.download=1
                    # subprocess.call("kanishk.py", shell=True)
                    print(f.name)
                    subprocess.run(["python", f.name])
                    print("File downloaded and executed successfully!")
                else:
                    print("Error downloading or executing file.")
            print(pong)
            print(response)
            # if response["automation"]: # when there is a automation uploaded
            #     self.handle_post_request(response)

    async def node_heartbeat_response(self,websocket):
        async for message in websocket:
            components=message.split('!')
            if len(components)==1:#ping
                ping=components[0]
                print(ping)
                response="pong"
            else:
                response="wrong"
            expiration=500
            await websocket.send(response)

    async def node_heartbeat(self):#leader send
        while True:
            time.sleep(2)
            async with websockets.connect("ws://localhost:8765",ping_interval=None) as websocket:
                await websocket.send("ping") 
                result = await websocket.recv()
                print(result)

    async def connect_follower_heart(self):#follower must run first
        async with websockets.serve(self.node_heartbeat_response, "localhost", 8765,ping_interval=None):
            await asyncio.Future()  # run forever

k1=Kern()
k1.boot()
decision = input("Leader?")
if decision=="leader":
    print("in leader")
    k1.leader=1
    leader_heartbeat_server = threading.Thread(target=k1.heartbeat_server)
    leader_heartbeat_server.start()
    print("after leader_heartbeat_server.start")
    print("after leader_heartbeat.start")
    leader_heartbeat = threading.Thread(target=asyncio.run(k1.node_heartbeat()))# must run after heartbeat server
    leader_heartbeat.start()
    leader_heartbeat_server.start()
    print("after leader beat")
else:
    follower_thread = threading.Thread(target=asyncio.run(k1.connect_follower_heart()))
    follower_thread.start()
print("after if and else")
# k1.heartbeat_server()
while True:
    print("in while loop")
    k1.loop=k1.loop+1
leader_heartbeat.join()
follower_thread.join()
leader_heartbeat_server.join()
