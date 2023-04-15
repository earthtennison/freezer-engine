
import socket

import numpy as np
import time
from custom_socket import CustomSocket
import json


host = socket.gethostname()
port = 10000


c = CustomSocket(host,port)
c.clientConnect()

print("Connecting to server...")
connected = False
while not connected:
    connected = c.clientConnect()




while True:
    user_input = input("You: ")
    res = c.req(user_input)
    print(res)