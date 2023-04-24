import boto3
import os
import requests
from botocore.handlers import disable_signing
import asyncio
import websockets
from botocore.exceptions import ClientError
import logging

async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)

async def get_module(websocket):
    async for message in websocket:
        # print(message)
        components=message.split('!')
        access_key=components[0]
        secret_key=components[1]
        bucket_name=components[2]
        module_name=components[3]
        expiration=500
        # create an S3 client
        s3_client = boto3.client('s3',region_name="us-east-2",aws_access_key_id=access_key,aws_secret_access_key=secret_key)
        try:
            url = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': module_name},
                                                    ExpiresIn=expiration)
        except ClientError as e:
            logging.error(e)
            return None
        # AWS S3 bucket encrypted URL and module name
        # bucket_url = "https://my-bucket.s3.amazonaws.com/"
        # encrypted_url = "https://s3.amazonaws.com/kms-encrypted-bucket/encrypted_file.txt"  # replace with your encrypted URL

        # construct the S3 object key
        # object_key = bucket_url + module_name
        # print("before header")
        # headers = {"Authorization": f"Bearer {access_key}"}
        # headers = {"Authorization": f"Bearer {secret_key}"}
        # download the module using requests library with decryption
        # print("resposne")
        # response = requests.get(encrypted_url,headers=headers)
        print("after resposne")
        
        response = requests.get(url,stream=True)
        if response is None:
            print("response is none")
            exit(1)
        # save the decrypted module locally
        with open(module_name, "wb") as f:
            f.write(response.content)
            print("after write")
        await websocket.send("module downloaded")

async def main():
    async with websockets.serve(get_module, "localhost", 8765,ping_interval=None):
        await asyncio.Future()  # run forever

asyncio.run(main())