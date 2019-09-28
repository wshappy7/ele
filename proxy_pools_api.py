'''
代理缓冲池
Author：陶永飞
Create time： 2019-01-26
Description： get_proxy() 从服务器获取代理IP
              abend_proxy() 通知服务器丢弃IP
              实例化class Proxy_pools的时候必须指定代理池名, eg. proxy_pools = Proxy_pools("dianping")
'''
import redis
import time
import logging
import redis


class Proxy_pools():
    redis_config = {
        "host": "",
        "port": "",
        "password": "",
        "keys": {
            # 代理池redis配置
            "proxy_pools": {
                "dianping": "proxy_pools:dianping",
                "dp_comment": "proxy_pools:dianping_comment",
                'dp_comment2': "proxy_pools:dianping_comment2",
                "dianshang": "proxy_pools:dianshang",
                "ele": "proxy_pools:ele",

            }
        }
    }

    def __init__(self, pools_name=None):
        self.pools_name = pools_name
        self.pool = redis.ConnectionPool(host=self.redis_config["host"],
                                         port=self.redis_config["port"],
                                         password=self.redis_config["password"],
                                         decode_responses=True)#这样写存的数据是字符串格式
        self.redis_conn = redis.Redis(connection_pool=self.pool)

    def get_proxy(self, pools_name=None, abend_ip=None):

        if pools_name is None:
            pools_name = self.pools_name
        if pools_name is None:
            logging.error("请输入pools name")
            return None
        else:
            if abend_ip:
                self.abend_proxy(abend_ip)

            redis_key = self.redis_config["keys"]["proxy_pools"][pools_name]
            while True:
                ip = self.redis_conn.brpoplpush(redis_key, redis_key, 5)
                if ip:
                    return ip
                else:
                    logging.warning("没有发现可用%s代理，等待5秒" % (pools_name))
                    time.sleep(5)

    def abend_proxy(self, proxy, pools_name=None):
        if pools_name is None:
            pools_name = self.pools_name
        if pools_name is None:
            logging.error("请输入pools name")
        else:
            redis_key = self.redis_config["keys"]["proxy_pools"][pools_name]
            return self.redis_conn.lrem(redis_key, 0, proxy)


if __name__ == "__main__":
    proxy_pools = Proxy_pools("ele")
    # 获取IP
    proxy = proxy_pools.get_proxy()
    print(proxy)
    # 启用IP
    proxy_pools.abend_proxy("113.101.138.45:44756")
