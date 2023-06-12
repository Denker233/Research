# DIoT:
##Overview:
The webserver heartbeats the leader node with link to acess the module using REST API.
W
Follower nodes heartbeats the leader node with running information so that leader can make load balancing decision based on the information with WebSocket API. 

The leader node would also send modules to other nodes if it decides to run it at there.

The load-balancing algorithms are weighted round robin and weighted-resource-based algorithm

## Key components: 
webserver.py</br> kernob.py</br> tool.py</br>

## How to Run
1. Open a terminal 
```python3 webserver.py```

2. Open another one
```python3 kernob.py```

And follow the prompt:
node_ID should be ```node1``` or ```node2``` or ```node3``` or you can add more node in read/write_IDs in webserver.py

Input ```leader``` for the first node (leader node must run first)

Input ```10``` or number of your choice for the max nodes that can be handled(the number might be needed in future)

3. Open other terminals:
```python3 kernob.py```

Input an node ID that show up in read/write_IDs in webserver.py

Input ```no``` or anything other than leader

## Next steps:
1. Completes the cache functionality: Remove cached modules if it times out.

2. Adjust parameters for load-balancing algorithm/Looking for better solutionss

3. Permission handling