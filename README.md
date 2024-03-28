# Get Grass Python Package
[![PyPi Version](https://img.shields.io/pypi/v/PyGrassClient?color=green)](https://pypi.python.org/pypi/PyGrassClient/)
[![Build Sphinx docs)](https://github.com/Confusion-ymc/PyGrassClient/actions/workflows/python-publish.yml/badge.svg)](https://github.com/Confusion-ymc/PyGrassClient/actions/workflows/python-publish.yml)

**This is a Python package for getting grass score.**

## 1. Installation
```
pip3 install PyGrassClient
```
## 2. Usage
### **1. Running with a Single Account**
 ```
 #!/usr/bin/env python
 
 from PyGrassClient import PyGrassClient
 # You only need a user_id or account and password
 asyncio.run(PyGrassClient(user_id="${userid}", user_name="${user_name}", password="${password}", proxy_url='${proxy_url}').connect_ws())
 ```
### **2. Running with Multiple Accounts**
 ```
 #!/usr/bin/env python
 
 from PyGrassClient import run_by_file
 
 run_by_file('accounts.txt')
 ```

### **3. Running with Docker**
 
1. `git clone https://github.com/Confusion-ymc/PyGrassClient.git`
2. Add an `accounts.txt` file
3. `docker compose up --build -d`

### 4. Format of the accounts.txt File
- Without Proxy Configuration
  - **Each line represents a single account configuration**
  - **If no proxy is used, then `user_id` alone in one line, in the format of `5242367b-d366-1234-987a-9ebd303fa8f5`**
  - **If you don't know the `user_id`, use the account and password----format as `test@qq.com---Aa@password`**
- With Proxy Configuration
  - **If using a proxy, add it to the end as `==proxy connection`----format as `5242367b-d366-1258-987a-9ebd303fa8f5==socks5://proxy.com:1080`**


- For example:
 ```text
5242367b-d366-1234-987a-9ebd303fa8f5==http://proxy.com:8080
5242367b-d366-1234-987a-9ebd303fa8f5
test@qq.com---Aa@password 
5242367b-d366-1258-987a-9ebd303fa8f5==socks5://proxy.com:1080
 ```