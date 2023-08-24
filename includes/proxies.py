import requests, logging
import time, urllib3
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
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        }
        
        proxies = {
            'http': f'socks5://{proxy}',
            'https': f'socks5://{proxy}'
        }

        logging.info("Check proxy: " + proxy)
        
        response = requests.get(url='https://www.bbb.com/', timeout = (15, 30),headers=headers, proxies=proxies, verify=False, allow_redirects=False)
        
        logging.info("code: " + str(response.status_code))
        
        if response.status_code >= 300 and response.status_code < 400:
            logging.info("redirect to: " + response.headers.get('location'))
        
        if response.status_code==200 or response.status_code == 302:
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
    
    if not useProxy:
        get_proxy_list()
        
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