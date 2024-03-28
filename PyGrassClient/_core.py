import asyncio
import json
import pathlib
import ssl
import sys
import threading
import time
import uuid

import websocket
from faker import Faker
from loguru import logger
from websocket import setdefaulttimeout

from PyGrassClient._async_core import AsyncGrassWs
from PyGrassClient.utils import parse_proxy_url, new_session, Status

logger.remove() 

logger.add(sys.stdout, level="INFO") 


class GrassWs:
    def __init__(self, user_id, proxy_url=None):
        self.user_id = user_id
        self.is_online = False
        self.reconnect_times = 0
        self.user_agent = Faker().chrome()
        self.device_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, proxy_url or ""))
        self.proxy_url = proxy_url
        self.ping_thread = None
        self.ws = self.init_ws()

    def init_ws(self):
        return websocket.WebSocketApp(
            "wss://proxy.wynd.network:4650/",
            header=[
                f"User-Agent: {self.user_agent}"],
            on_error=self.on_error,
            on_message=self.on_message,
            on_open=self.on_open,
            on_close=self.on_close
        )

    def info(self, message):
        return f'\n------\n[{message}]\n[user_id: {self.user_id}]\n[proxy_url: {self.proxy_url}]\n[device_id: {self.device_id}]\n------\n'

    def send_ping(self, wsapp):
        while self.is_online:
            time.sleep(20)
            try:
                send_message = json.dumps(
                    {"id": str(uuid.uuid4()), "version": "1.0.0", "action": "PING", "data": {}})
                wsapp.send(send_message)
                logger.debug(f'send {send_message}')
            except Exception as e:
                logger.error(
                    f'[user_id: {self.user_id}] [proxy_url: {self.proxy_url}] ping error: {e}')
                self.ws.close()
                break
        self.is_online = False
        self.ping_thread = None

    def on_open(self, wsapp):
        self.reconnect_times += 1
        logger.debug(self.info(f'Connect open'))

    def on_close(self, wsapp, close_status_code, close_msg):
        self.is_online = False
        logger.error(self.info(f'Connect close: {close_msg}'))

    def on_error(self, wsapp, err):
        self.is_online = False
        logger.error(self.info(f'Connect error: {err}'))

    def on_message(self, wsapp, message):
        message = json.loads(message)
        logger.debug(f'recv {message}')
        if message.get("action") == "AUTH":
            auth_response = {
                "id": message["id"],
                "origin_action": "AUTH",
                "result": {
                    "browser_id": self.device_id,
                    "user_id": self.user_id,
                    "user_agent": self.user_agent,
                    "timestamp": int(time.time()),
                    "device_type": "extension",
                    "version": "3.3.0"
                }
            }
            logger.debug(f'send {auth_response}')
            wsapp.send(json.dumps(auth_response))
            self.is_online = True
            logger.info(self.info(f"连接成功 连接次数: {self.reconnect_times}"))
            self.ping_thread = threading.Thread(
                target=self.send_ping, args=(self.ws,), daemon=True)
            self.ping_thread.start()
        elif message.get("action") == "PONG":
            pong_response = {"id": message["id"], "origin_action": "PONG"}
            logger.debug(f'send {pong_response}')
            wsapp.send(json.dumps(pong_response))

    def run(self):
        setdefaulttimeout(30)
        if self.proxy_url:
            proxy_type, http_proxy_host, http_proxy_port, http_proxy_auth = parse_proxy_url(
                self.proxy_url)
        else:
            proxy_type = http_proxy_host = http_proxy_port = http_proxy_auth = None
        logger.info(self.info('Run start'))
        while True:
            self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE}, proxy_type=proxy_type,
                                http_proxy_host=http_proxy_host,
                                http_proxy_port=http_proxy_port, http_proxy_auth=http_proxy_auth,
                                reconnect=5)
            self.is_online = False
            while self.ping_thread is not None:
                time.sleep(1)
            self.ws = self.init_ws()


class PyGrassClient:
    def __init__(self, *, user_name=None, password=None, user_id=None, proxy_url=None):
        assert user_id or (user_name and password), Exception(
            'must set user_name and password or set user_id!')
        self.user_name = user_name
        self.password = password
        self.user_id = user_id
        self.proxy_url = proxy_url
        self.session = new_session(self.proxy_url)
        self.ws = AsyncGrassWs(self.user_id, self.proxy_url)
        self.dashboard = {}
        # self.is_login = False

    def login(self):
        assert (self.user_name and self.password), Exception(
            'must set user_name and password!')
        json_data = {
            'user': self.user_name,
            'password': self.password,
        }
        response = self.session.post(
            'https://api.getgrass.io/auth/login', json=json_data).json()
        if response["status"] == "success":
            self.user_id = response["data"]["id"]
        else:
            raise Exception(f'login fail, [{self.user_name}, {self.password}]')

    
    async def connect_ws(self):
        if not self.user_id:
            self.login()
        self.ws.user_id = self.user_id
        await self.ws.run()


def run_by_file(acc_file_path):
    asyncio.run(aio_run_by_file(acc_file_path))


async def aio_run_by_file(acc_file_path):
    all_clients = load_account_by_file(acc_file_path)
    for client in all_clients:
        asyncio.create_task(client.connect_ws())
        await asyncio.sleep(1)
    n = 0
    while n < 60 * 60 * 4:
        if n % 10 == 0:
            logger.info(
                f'online: {len(list(filter(lambda x: x.ws.status == Status.connected, all_clients)))} all: {len(all_clients)}')
        n += 1
        await asyncio.sleep(1)


def load_account_by_file(acc_file_path):
    all_clients = []
    index = 0
    with open(acc_file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if "==" in line:
                user_id, proxy_url = line.split('==')
            else:
                user_id, proxy_url = line, None
            if "---" in user_id:
                user_name, password = user_id.split('---')
                user_id = None
            else:
                user_name = password = None
            proxy_url = proxy_url or None
            index += 1
            client = PyGrassClient(
                user_id=user_id, user_name=user_name, password=password, proxy_url=proxy_url)
            logger.info(f'[{index}] [user_id: {user_id}] [proxy: {proxy_url}]')
            all_clients.append(client)
    return all_clients
