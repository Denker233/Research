import asyncio
import websockets
import logging
import boto3
import requests
from botocore.exceptions import ClientError

async def hello():
    bucket_name = "moduleiot"
    object_name = "test.py"
    access_key = "AKIA256SBCN3YKGGO4VR"
    secret_key = "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"
    # expiration = 500
    s3_client = boto3.client('s3',region_name="us-east-2",aws_access_key_id=access_key,aws_secret_access_key=secret_key)
    async with websockets.connect("ws://localhost:8765",ping_interval=None) as websocket:
        await websocket.send(access_key+"!"+secret_key+"!"+bucket_name+"!"+object_name) #url
        result = await websocket.recv()
        print(result)
    # account_name = "denker233"
    # ID = "9fb428d9-e5fe-40d6-857c-ad8f5813bcd7"
    # port = 6262
    # hostname = "csel-kh1250-10"
    # url = 'http://localhost:8000/post'
    # container = "diotauto"
    # bolb = "test.py"
    # data = {"ID": ID, "container": container,"bolb":bolb,"account_name":account_name}
    # headers = {"Authorization": "Bearer my_token"}

    # response = requests.post(url, data=data)
    # response = requests.post(url, data=data, headers=headers)
    # print(response.text)

    

asyncio.run(hello())