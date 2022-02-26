import random
import os
import json
from config.settings.base import BASE_DIR

proxy_file = os.path.join(BASE_DIR, "secrets/proxys.json")

with open(proxy_file) as f:
    proxy = json.loads(f.read())["proxy"]
proxies = proxies = {"https": random.choice(proxy)}
