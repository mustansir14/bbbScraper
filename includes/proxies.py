import requests, logging
import time
from random import choice

proxyList = None
proxyListNextDownload = None

def get_proxy_list():
    global proxyList, proxyListNextDownload
    
    if proxyList is None or proxyListNextDownload < time.time():        
        url = 'http://94.140.123.40:25000/'
        
        logging.info("Download proxy list: " + url )
        
        r = requests.get(url, timeout=10)
        
        if r.status_code==200:
            lines = r.text.splitlines()
            lines = map (lambda x: x.strip(), lines)
            lines = list (filter(None, lines))
            
            if not lines:
                raise Exception ('No proxies in list')
                
            proxyList = lines
            proxyListNextDownload = time.time() + 6000  
        else:
            raise Exception ('Error with connecting to the proxy-list')
            

def func_chunk_array(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def checkSocks5Proxy(proxy):
    try:
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'}
        
        proxies = {
            'http': f'socks5://{proxy}',
            'https': f'socks5://{proxy}'
        }

        logging.info("Check proxy: " + proxy)
        
        response = requests.get(url='https://www.bbb.com/', headers=headers, proxies=proxies, verify=False)
        
        logging.info("code: " + str(response.status_code))
        
        if response.status_code==200:
            return True
    except Exception as e:
        logging.info(str(e))
        pass
    
    return False


# def write_file(filename, src):
#     with open(filename, 'a', encoding='utf-8') as file:
#         file.write(src+'\n')  




def getProxy(useProxy=None):
    global proxyListNextDownload
    
    get_proxy_list()
    
    if not useProxy:
        proxy = None
        while len(proxyList) > 0:
            get_proxy_list()
            proxy = choice(proxyList)
            if checkSocks5Proxy(proxy):
                break
            proxyList.remove(proxy)
    else:
        proxy = useProxy
        
    parts = proxy.split(":")
    
    # proxy=PROXY, proxy_port=PROXY_PORT, proxy_user=PROXY_USER, proxy_pass=PROXY_PASS, proxy_type=PROXY_TYPE
    return {
        'proxy': parts[0],
        'proxy_port': parts[1],
        'proxy_user': None,
        'proxy_pass': None,
        'proxy_type': 'socks5'
    }