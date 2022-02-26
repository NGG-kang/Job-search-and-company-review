from bs4 import BeautifulSoup
import requests
import django
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(os.path.dirname(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
from crawling.models import JobPlanet
from crawling.functions.kreditjob import kreditjob_crawling
from crawling.functions.proxy import proxies


def find_content(soup):
    company_name = (
        soup.find("div", {"class": "company_info_box"})
        .find("a")
        .text.replace("(주)", "")
    )
    data_json = soup.find("ul", {"class": "basic_info_more"})
    company_info = dict()
    for data in data_json:
        header = data.find("dt")
        content = data.find("dd")
        if header == -1:
            continue
        company_info[header.text.strip()] = content.text.strip()
    return (company_name, company_info)


def jobplanet(page):
    print(
        "---------------------------------JOBPLNET----------------------------------------"
    )
    print(page)
    while True:
        try:
            try:
                j = JobPlanet.objects.get(company_pk=page)
                print("skip")
                break
                j.name = company_name
                j.data = company_info
                j.save()
            except JobPlanet.DoesNotExist:
                search_url = f"https://www.jobplanet.co.kr/companies/{page}/landing/"
                html = requests.get(search_url, allow_redirects=False)
                if html.status_code in (302, 404):
                    break
                soup = BeautifulSoup(html.content, "lxml")
                company_name, company_info = find_content(soup)
                print(company_name)
                print(company_info)
                JobPlanet(name=company_name, company_pk=page, data=company_info).save()
            print(
                "---------------------------------JOBPLNET----------------------------------------"
            )
            kreditjob_crawling(company=company_name)
            break
        except Exception as e:
            print(e)
