import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(os.path.dirname(BASE_DIR))
from celery import shared_task
from crawling.models import JobPlanet, KreditJob, Saramin
import json
from proxy import proxies
from bs4 import BeautifulSoup
import requests
import re


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


@shared_task
def jobplanet(name):
    print(
        "---------------------------------JOBPLNET----------------------------------------"
    )
    for _ in range(5):
        try:
            search_url = f"https://www.jobplanet.co.kr/autocomplete/autocomplete/suggest.json?term={name}"
            html = requests.get(search_url, allow_redirects=False, proxies=proxies)
            companies = json.loads(html.content)["companies"]
            if html.status_code in (302, 404):
                break
            # 업데이트 할거면 풀기
            # print(company_name)
            # print(company_info)
            for company in companies:
                name = company["name"]
                _id = company["id"]
                try:
                    j = JobPlanet.objects.get(company_pk=_id)
                    print("skip")
                    continue
                    j.name = company_name
                    j.data = company_info
                    j.save()
                except JobPlanet.DoesNotExist:
                    search_url = f"https://www.jobplanet.co.kr/companies/{_id}/landing/"
                    html = requests.get(
                        search_url, allow_redirects=False, proxies=proxies
                    )
                    soup = BeautifulSoup(html.content, "lxml")
                    company_name, company_info = find_content(soup)
                    print(company_name)
                    print(company_info)
                    JobPlanet(
                        name=company_name, company_pk=_id, data=company_info
                    ).save()
                print(
                    "---------------------------------JOBPLNET----------------------------------------"
                )
            break
        except Exception as e:
            print(e)
        finally:
            kreditjob_crawling(company=company_name)


@shared_task
def get_saramin_company(name):
    page = 1
    while True:
        resq = requests.get(
            f"https://www.saramin.co.kr/zf_user/search/company?searchword={name}&page={page}&searchType=search&pageCount=30&mainSearch=n",
            proxies=proxies,
        )
        soup = BeautifulSoup(resq.content, "lxml")
        search_list = soup.find_all("div", class_="item_corp")
        if not search_list:
            break
        for company in search_list:
            try:
                corp_name = company.find("h2", class_="corp_name")
                name = corp_name.find("a")
                url = name["href"]
                name = name.text.strip()

                company_pk = url.split("csn=")[-1]
                try:
                    Saramin.objects.get(company_pk=company_pk)
                except Saramin.DoesNotExist:
                    data = {}
                    corp_info = company.find("div", class_="corp_info")
                    data_list = corp_info.find_all("dl")
                    address = ""
                    for val in data_list:
                        key = val.find("dt").text.strip()
                        value = re.sub(r" {2,}", "", val.find("dd").text.strip())
                        if key == "기업주소":
                            address = value
                        data[key] = value
                    Saramin(
                        name=name, company_pk=company_pk, address=address, data=data
                    ).save()
            except:
                pass
        page += 1


def kreditjob_crawling(company):
    print(
        "---------------------------------KREDITJOB----------------------------------------"
    )
    search_url = f"https://www.kreditjob.com/api/search/autocomplete"
    search_response = json.loads(
        requests.get(
            search_url,
            params=[("q", company), ("index", 0), ("size", 5)],
            proxies=proxies,
        ).content
    )
    search_response = search_response.get("docs")

    print("-----------------검색---------------------")
    for search_company in search_response:
        print(search_company)
        CMPN_NM = search_company["CMPN_NM"]
        WKP_ADRS = search_company["WKP_ADRS"]
        PK_NM_HASH = search_company["PK_NM_HASH"]
        try:
            k = KreditJob.objects.get(company_pk=PK_NM_HASH)
            print("skip")
            break
            k.name = CMPN_NM
            k.address = WKP_ADRS
            k.company_base_content = company_base_content
            k.company_info_data = company_info_data
            k.company_jobdam = company_jobdam
            k.save()
        except KreditJob.DoesNotExist:
            company_base_content = json.loads(
                requests.get(
                    f"https://www.wanted.co.kr/api/v1/company_briefs?kreditjob_pk={PK_NM_HASH}",
                    proxies=proxies,
                ).content
            )
            # POST
            # 기업 연봉포함 정보
            # data
            data = {"PK_NM_HASH": PK_NM_HASH}
            company_info_data = json.loads(
                requests.post(
                    "https://www.kreditjob.com/api/company/companyPage",
                    data=data,
                    proxies=proxies,
                ).content
            )
            # POST
            # 기업 잡담
            data = {"PK_NM_HASH": ["PK_NM_HASH", PK_NM_HASH]}
            company_jobdam = json.loads(
                requests.post(
                    "https://www.kreditjob.com/api/jobdom/multiFilter/1/10",
                    data=data,
                    proxies=proxies,
                ).content
            )
            # print("-----------------기업기본정보---------------------")
            # print(company_base_content)
            # print("-----------------기업연봉포함정보---------------------")
            # print(company_info_data)
            # print("-----------------기업잡담---------------------")
            # print(company_jobdam)

            print("-----------------기업기본정보---------------------")
            print(company_base_content)
            KreditJob(
                name=CMPN_NM,
                address=WKP_ADRS,
                company_pk=PK_NM_HASH,
                company_base_content=company_base_content,
                company_info_data=company_info_data,
                company_jobdam=company_jobdam,
            ).save()


@shared_task
def get_saramin_company(name):
    page = 1
    while True:
        resq = requests.get(
            f"https://www.saramin.co.kr/zf_user/search/company?searchword={name}&page={page}&searchType=search&pageCount=30&mainSearch=n#company_info",
            proxies=proxies,
        )
        soup = BeautifulSoup(resq.content, "lxml")
        search_list = soup.find_all("div", class_="item_corp")
        if not search_list:
            break
        while True:
            try:
                for company in search_list:

                    corp_name = company.find("h2", class_="corp_name")
                    name = corp_name.find("a")
                    url = name["href"]
                    name = name.text.strip()

                    company_pk = url.split("csn=")[-1]
                    data = {}
                    print(url)
                    corp_info = company.find("div", class_="corp_info")
                    data_list = corp_info.find_all("dl")
                    address = ""
                    for val in data_list:
                        key = val.find("dt").text.strip()
                        value = re.sub(r" {2,}", "", val.find("dd").text.strip())
                        if key == "기업주소":
                            address = value
                        data[key] = value
                    Saramin(
                        name=name, company_pk=company_pk, address=address, data=data
                    ).save()
                break
            except:
                pass

        page += 1
