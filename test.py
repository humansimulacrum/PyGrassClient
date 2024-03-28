#!/usr/bin/env python
import asyncio

from PyGrassClient import PyGrassClient
# You only need a user_id or account and password
asyncio.run(PyGrassClient(
    user_id="5bf25176-fe0f-445f-aa12-5bad3993f185",  proxy_url='socks5://31.211.130.237:8192').connect_ws())



# 
# 
# 184.95.220.42:1080
# 45.138.87.238:1080

# asyncio.run(PyGrassClient(
#     user_id="5bf25176-fe0f-445f-aa12-5bad3993f185").connect_ws())
