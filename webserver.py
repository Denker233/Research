import asyncio
import websockets
import logging
import boto3
import requests
from botocore.exceptions import ClientError
from flask import Flask, request

app = Flask(__name__)





def boost_handler(request):
    device_ID = request.form["ID"]
    device_name=request.form["device_name"]
    ##check credential has't been implemented
    print("here")
    account_name = "denker233"
    ID = "9fb428d9-e5fe-40d6-857c-ad8f5813bcd7"
    port = 6262
    hostname = "csel-kh1250-10"

    # url = 'http://localhost:8000/post'
    container = "diotauto"
    bolb = "test.py"
    data = {"ID": ID, "container": container,"bolb":bolb,"account_name":account_name}
    print(data)
    # headers = {"Authorization": "Bearer my_token"}
    # return 'Success'
    return data
    # response = requests.post(url, data=data)
    # response = requests.post(url, data=data, headers=headers)
    # print(response.text)


@app.route('/post', methods=['POST'])
def post_handler():
    if request.form["type"] == "boot":
        data = boost_handler(request)
        return data
    elif request.form["type"] == "beat": 
        print("in beat handler")
        data = {"result":"pong from server"}
        #if there is a automation uploaded
        return data 
    return "success"
    



    
if __name__ == '__main__':
    app.run("localhost",port=8000)
   