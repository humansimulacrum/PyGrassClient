#!/usr/bin/env python
import asyncio

from PyGrassClient import PyGrassClient
# You only need a user_id or account and password
asyncio.run(PyGrassClient(
    user_id="5bf25176-fe0f-445f-aa12-5bad3993f185",  proxy_url='socks5://31.211.130.237:8192').connect_ws())

