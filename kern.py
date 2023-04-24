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



ID = "xxxx"
device_name="node1"
loop=0
leader=0



app = Flask(__name__)
# @app.route('/post', methods=['POST'])
def download_blob_to_file(blob_service_client: BlobServiceClient, container_name, bolb):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=bolb)
    with open(file=os.path.join('/home/tian0138/csci-5105/Research', bolb), mode="wb") as sample_blob:
        download_stream = blob_client.download_blob()
        sample_blob.write(download_stream.readall())
def handle_post_request(response):
    # Get the data from the request body
    print("in download")
    ID = response["ID"]
    container = response["container"]
    bolb = response["bolb"]
    account_name = response["account_name"]
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    blob_service_client = BlobServiceClient(account_url=account_url)
    download_blob_to_file(blob_service_client,container,bolb)
    # Process the data...
    return 'Success'

def boot():
    url = 'http://localhost:8000/post'
    data = {"type":"boot", "ID": ID, "device_name": device_name}
    response = requests.post(url, data=data)
    response = response.json()
    print(response)
    handle_post_request(response)

def heartbeat_server():
    while True:
        time.sleep(2)
        url = 'http://localhost:8000/post'
        data = {"ID": ID, "device_name": device_name}
        response = requests.post(url, data=data)
        print(response)
        

async def node_heartbeat_response(websocket):
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

async def node_heartbeat():#leader send 
    async with websockets.connect("ws://localhost:8765",ping_interval=None) as websocket:
        await websocket.send("ping") 
        result = await websocket.recv()
        print(result)

async def main():#follower must run first
    async with websockets.serve(node_heartbeat_response, "localhost", 8765,ping_interval=None):
        await asyncio.Future()  # run forever


boot()
decision = input("Leader node or not?")
if decision=="leader":
    print("in leader")
    leader=1
    leader_heartbeat = threading.Thread(target=heartbeat_server)
    leader_heartbeat.start()
    while True:
        time.sleep(1)
        asyncio.run(node_heartbeat())
    # leader_heartbeat = threading.Thread(target=asyncio.run(node_heartbeat))
else:
    asyncio.run(main())#follower must run first
    # follower_thread = threading.Thread(target=asyncio.run(connect_follower_heart))
while True:
    loop+=1
leader_heartbeat.join()
follower_thread.join()

