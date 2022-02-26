import django
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(os.path.dirname(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


from bs4 import BeautifulSoup
import requests
import re

from crawling.models import JobKorea
from crawling.functions.proxy import proxies
import random


def get_jobkorea_company(name):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        "referer": "https://www.google.com/",
    }
    page = 1
    while True:
        resq = requests.get(
            f"https://www.jobkorea.co.kr/Search/?stext={name}&tabType=corp&Page_No={page}",
            proxies=proxies,
            headers=headers,
            timeout=5,
        )
        soup = BeautifulSoup(resq.content, "lxml")
        search_list = soup.find("div", class_="corp-info")
        search_list = search_list.find("div", class_="lists")
        search_list = search_list.find_all("li", class_="list-post")
        if not search_list:
            break
        for company in search_list:
            corp_name = company.find("a", class_="name dev_view")
            name = corp_name["title"].strip()
            url = f"https://www.jobkorea.co.kr{corp_name['href']}"

            company_pk = url.split("/")[-1]
            resq = requests.get(url, proxies=proxies, headers=headers, timeout=5)
            soup = BeautifulSoup(resq.content, "lxml")
            data = {}
            corp_info = soup.find(
                "div", class_="company-infomation-row basic-infomation"
            )
            corp_info = corp_info.find(
                "div", class_="company-infomation-container basic-infomation-container"
            )
            data_list = corp_info.find_all("tr")
            address = ""
            for val in data_list:
                keys = val.find_all("th")
                keys = [i.text.strip() for i in keys]
                values = val.find_all("td")
                values = [re.sub(r" {2,}", "", i.text.strip()) for i in values]
                datas = dict(zip(keys, values))
                if "주소" in datas:
                    address = datas["주소"]
                data = {**data, **datas}
            print(data)
            print(address)
            search_address = address.split(" ")
            if len(search_address) >= 2:
                search_address = f"{search_address[0]} {search_address[1]}"
            else:
                search_address = address
            print(search_address)
            # JobKorea(
            #     name=name,
            #     company_pk=company_pk,
            #     address=address,
            #     data=data,
            #     search_address="",
            # ).save()
        page += 1
        break


get_jobkorea_company("트레이디")
