import requests
from proxy_pools_api import Proxy_pools
class CheckIp():
    def check_ip(self):

        h = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'}

        proxy_pools = Proxy_pools("ele")
        url = "https://www.baidu.com/"
        while True:
            proxy = proxy_pools.get_proxy()
            proxies = {
                "http": f"http://{proxy}",
                "https": f"https://{proxy}"
            }
            try:
                response=requests.get(url=url,proxies=proxies,headers=h,verify=False)
                print(response)
                print(proxy + 'ip有效')
                return proxies

            except Exception as e:
                print(e)
                print(proxy+'ip失效')
                proxy_pools.abend_proxy(proxy)
                print(proxy+'已删除')
if __name__ == '__main__':

    proxies=CheckIp().check_ip()
    print(proxies)