from proxy.proxy import Proxy
from client.strategy import Strategy

if __name__ == "__main__":
    s = Strategy()
    s.start()
    s.join()
    print(s.percent_change)
    # Proxy()
