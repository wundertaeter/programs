from selenium import webdriver
from selenium.webdriver.chrome.options import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType
from pandas import read_html
import time
from random import shuffle
import requests

co = webdriver.ChromeOptions()
co.add_argument("log-level=3")
co.add_argument("ignore-certificate-errors")

def get_proxies(co=co):
    header = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
    }

    r = requests.get('https://free-proxy-list.net/', headers=header)

    proxy_df = read_html(r.text)[0]
    proxy_df = proxy_df[proxy_df['Https'] == 'yes'][['IP Address', 'Port']]
    proxy_df["Port"] = proxy_df["Port"].astype(int)
    proxy_df = proxy_df.apply(lambda x: ':'.join(x.astype(str)),axis=1)
    return list(proxy_df.values)


ALL_PROXIES = get_proxies()


def proxy_driver(PROXIES, co=co):
    if PROXIES:
        pxy = PROXIES[-1]
    else:
        print("--- Proxies used up (%s)" % len(PROXIES))
        #PROXIES = get_proxies()
        exit()

    co.add_argument('--proxy-server=%s' % pxy)
    driver = webdriver.Chrome('immoscout/chromedriver', chrome_options=co)

    return driver



pd = proxy_driver(ALL_PROXIES)

while True:
    try:
        print('starting..')
        url = 'https://whatismyipaddress.com/de/meine-ip'
        pd.get(url)
        time.sleep(2)
        2/0
    except Exception as e:
        print(e)
        pd.close()
        new = ALL_PROXIES.pop()
        
        pd = proxy_driver(ALL_PROXIES)
        print("--- Switched proxy to: %s" % new)
        time.sleep(1)
