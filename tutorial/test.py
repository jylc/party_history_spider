import requests

url = 'www.ncist.edu.cn'
proxies1 = {"http": "http://127.0.0.1:8181", "https": "http://127.0.0.1:8181"}

rsp0 = requests.get(url)
print(rsp0)
print(rsp0.status_code)
