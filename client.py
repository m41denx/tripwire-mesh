import hashlib
import os
import requests
import subprocess
import sys
import time

TOKEN = os.environ.get("token")
SERVER = os.environ.get("server")
CONF_HASH = ""


def gethash(data=None):
    if data is None:
        with open("/etc/wireguard/wg0.conf", "w+") as f:
            data = f.read()
    md5 = hashlib.md5()
    md5.update(data.encode('utf-8'))
    return md5.hexdigest()


def get_ip():
    return requests.get('https://api.ipify.org').text.replace('\n', '')


def gen_privkey():
    return subprocess.check_output(['wg', 'genkey']).decode('utf-8').replace('\n', '')


def get_hostname():
    return subprocess.check_output(['hostname']).decode('utf-8').replace('\n', '')


def update_peer(address, port="1080"):
    conf = {
        "private_key": gen_privkey(),
        "address": address,
        "endpoint": get_ip(),
        "port": port,
        "name": get_hostname()
    }
    r = requests.post(f"{SERVER}/update", json=conf)
    print(r.text)
    return r.status_code == 200


def new_peer(address, port="1080"):
    conf = {
        "private_key": gen_privkey(),
        "address": address,
        "endpoint": get_ip(),
        "port": port,
        "name": get_hostname()
    }
    r = requests.post(f"{SERVER}/new", json=conf)
    print(r.text)
    return r.status_code == 200


def fetch_config():
    r = requests.get(f"{SERVER}/getconf/{get_hostname()}")
    if r.status_code!=200:
        return ""
    return r.text


def restartwg(data=None):
    if data is not None:
        with open("/etc/wireguard/wg0.conf", "w") as f:
            f.write(data)
    subprocess.call(['service', 'wg-quick@wg0', 'restart'])


def run():
    while True:
        conf = fetch_config()
        h1 = gethash()
        h2 = gethash(conf)
        if h1 != h2:
            restartwg(conf)
            print("Updating config")
        time.sleep(60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        run()
    else:
        if sys.argv[1] == "update":
            update_peer(sys.argv[2], sys.argv[3])
        elif sys.argv[1] == "new":
            new_peer(sys.argv[2], sys.argv[3])
