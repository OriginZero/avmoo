from selenium import webdriver
from selenium.webdriver.common.proxy import *
import urllib.request
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
}
proxies = {'http': 'socks5://127.0.0.1:7890',
           'https': 'socks5://127.0.0.1:7890'}
url = 'https://javdb.com/videos/search_autocomplete.json?q=SDSS-226'

proxy_handler = urllib.request.ProxyHandler(proxies)
opener = urllib.request.build_opener(proxy_handler)
request = urllib.request.Request(url, headers=headers)
res = opener.open(request)

print(json.loads(res.read()))
