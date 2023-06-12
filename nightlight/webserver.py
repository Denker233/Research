import asyncio
import websockets
import logging
import boto3
import requests
from botocore.exceptions import ClientError
from flask import Flask, request

app = Flask(__name__)


read_IDs = ["node1","node2","node3"]
write_IDs = ["node1","node2","node3"]
node_map = []
module_name = ""


def boost_handler(request):
    # device_ID = request.form["ID"]
    node_ID=request.form["node_ID"]
    credential = "xxxx"
    print("node ID: {}".format(node_ID))
    ##check credential has't been implemented
    node = {
        'node_ID': node_ID,
        'running_modules': [],
        'cached_modules': []
    }
    node_map.append(node)
    print("here")
    data = {"credential":credential}
    print(data)
    # headers = {"Authorization": "Bearer my_token"}
    # return 'Success'
    return data
    
        

@app.route('/post', methods=['POST'])
def post_handler():
    global module_name
    if request.form["node_ID"] in read_IDs or request.form["node_ID"] in write_IDs:
        if request.form["type"] == "boot":
            data = boost_handler(request)
            return data
        elif request.form["type"] == "beat": #need modification to check credential
            print("in beat handler")
            for node in node_map:
                if node["node_ID"]==request.form["node_ID"]:
                    print("two IDs are equal")
                    print(request.form.get("running_modules"))
                    #if there is a automation uploaded, it should trigger the change of module name then it will be sent to the leader node when the next heartbeat happen
                    module_name = "minrui"
                    print("before data is formated")
                    data = {"url":"https://dcsg-diot-frontend-kanishk-k.vercel.app/api/fetchModule/{}.py".format(module_name),"result":"pong from server","module_name":module_name}
                    print("link send to leader")
                    return data
    else:
        print("no read or write permission!!")
    



    
if __name__ == '__main__':
    app.run("localhost",port=8001)
   