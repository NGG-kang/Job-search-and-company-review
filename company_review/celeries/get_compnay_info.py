import json
import re
import traceback
from datetime import timedelta

import requests
from bs4 import BeautifulSoup
from crawling.models import JobPlanet, KreditJob, Saramin
from django.utils import timezone
from proxy import proxies


def process_name(name):
    name = re.sub(r"\([^)]*\)", "", name)
    name = re.sub(r"（[^)]*）", "", name)

    name = re.sub(r"[^a-zA-Z0-9가-힣]", "", name)
    name = re.sub(r"주식회사", "", name)
    return name.strip()


def get_jobplanet_company(name, update=False):
    def find_content(soup):
        company_name = (
            soup.find("div", {"class": "company_info_box"})
            .find("a")
            .text.replace("(주)", "")
        )
        company_name = process_name(company_name)
        data_json = soup.find("ul", {"class": "basic_info_more"})
        company_info = dict()
        for data in data_json:
            header = data.find("dt")
            content = data.find("dd")
            if header == -1:
                continue
            company_info[header.text.strip()] = content.text.strip()
        return (company_name, company_info)

    def get_company_content(_id):
        search_url = f"https://www.jobplanet.co.kr/companies/{_id}/landing/"
        html = requests.get(search_url, allow_redirects=False, proxies=proxies)
        soup = BeautifulSoup(html.content, "lxml")
        company_name, company_info = find_content(soup)
        address = company_info["주소"]
        _address = address.replace("본사: ", "")
        _address = address.split(" ")
        if len(_address) >= 2:
            _address[0] = _address[0].replace("광역시", "")
            _address[0] = _address[0].replace(",", "")
            search_address = f"{_address[0]} {_address[1]}"
        else:
            search_address = address
        return (company_name, company_info, address, search_address)

    print(
        "---------------------------------JOBPLNET----------------------------------------"
    )
    search_url = f"https://www.jobplanet.co.kr/autocomplete/autocomplete/suggest.json?term={name}"
    html = requests.get(search_url, allow_redirects=False, proxies=proxies)
    companies = json.loads(html.content)["companies"]
    if html.status_code not in (302, 404):
        # 업데이트 할거면 풀기
        for company in companies:
            try:
                name = company["name"]
                _id = company["id"]
                try:
                    j = JobPlanet.objects.get(company_pk=_id)
                    now = timezone.now()
                    if now < (j.updated + timedelta(days=7)):
                        print(name, "7일 지나지 않음, skip")
                        continue
                    (
                        company_name,
                        company_info,
                        address,
                        search_address,
                    ) = get_company_content(_id)
                    j.name = process_name(company_name)
                    j.company_pk = _id
                    j.data = company_info
                    j.address = address
                    j.search_address = search_address
                    j.save()
                    print(company_name, "업데이트")
                except JobPlanet.DoesNotExist:
                    (
                        company_name,
                        company_info,
                        address,
                        search_address,
                    ) = get_company_content(_id)
                    JobPlanet(
                        name=process_name(company_name),
                        company_pk=_id,
                        data=company_info,
                        address=address,
                        search_address=search_address,
                    ).save()
                    print("jobplanet", company_name, "저장")
            except Exception as e:
                print(search_url)
                print(traceback.print_exc())


def get_saramin_company(name, update=False):
    def get_company_content(soup):
        data = {}
        corp_info = soup.find("div", class_="corp_info")
        if not corp_info:
            address = ""
            _address = ""
            data = {}
            return address, _address, data
        data_list = corp_info.find_all("dl")
        
        address = ""
        _address = ""
        for val in data_list:
            key = val.find("dt").text.strip()
            value = re.sub(r" {2,}", "", val.find("dd").text.strip())
            if key == "기업주소":
                address = value
                _address = address.split(" ")
                if len(_address) >= 2:
                    _address[0] = _address[0].replace("광역시", "")
                    _address[0] = _address[0].replace(",", "")
                    _address = f"{_address[0]} {_address[1]}"
                else:
                    _address = address
            data[key] = value
        return address, _address, data

    page = 1
    while True:
        search_url = f"https://www.saramin.co.kr/zf_user/search/company?searchword={name}&page={page}"
        resq = requests.get(
            search_url,
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
                name = process_name(name)
                company_pk = url.split("csn=")[-1]
                try:
                    s = Saramin.objects.get(company_pk=company_pk)
                    now = timezone.now()
                    if now < (s.updated + timedelta(days=7)):
                        print(name, "7일 지나지 않음, skip")
                        continue
                    address, search_address, data = get_company_content(soup)
                    s.name = name
                    s.company_pk = company_pk
                    s.address = address
                    s.data = data
                    s.search_address = search_address
                    s.save()
                except Saramin.DoesNotExist:
                    address, search_address, data = get_company_content(soup)
                    Saramin(
                        name=name,
                        company_pk=company_pk,
                        address=address,
                        data=data,
                        search_address=search_address,
                    ).save()
                    print("saramin", name, "저장")
            except:
                print(search_url)
                print(traceback.print_exc())
        page += 1


def get_kreditjob_company(company, update=False):
    def get_company_content(PK_NM_HASH):
        company_info = json.loads(
            requests.get(
                f"https://www.kreditjob.com/api/company/{PK_NM_HASH}/info",
                proxies=proxies,
            ).content
        )
        company_summary = json.loads(
            requests.get(
                f"https://www.kreditjob.com/api/company/{PK_NM_HASH}/summary",
                proxies=proxies,
            ).content
        )
        company_salaries = json.loads(
            requests.get(
                f"https://www.kreditjob.com/api/company/{PK_NM_HASH}/salaries",
                proxies=proxies,
            ).content
        )
        company_employee = json.loads(
            requests.get(
                f"https://www.kreditjob.com/api/company/{PK_NM_HASH}/employee",
                proxies=proxies,
            ).content
        )
        company_status = json.loads(
            requests.get(
                f"https://www.kreditjob.com/api/company/{PK_NM_HASH}/states",
                proxies=proxies,
            ).content
        )

        # new 크레딧잡 정보들
        company_base_content = {
            "company_info": company_info,
            "company_summary": company_summary,
            "company_salaries": company_salaries,
            "company_employee": company_employee,
            "company_status": company_status
        }

        # POST
        # 기업 연봉포함 정보
        # 너무 옛날 정보들 포함이라 미적용
        # data
        data = {"PK_NM_HASH": PK_NM_HASH}
        company_info_data = ""
        # company_info_data = json.loads(
        #     requests.post(
        #         "https://www.kreditjob.com/api/company/companyPage",
        #         data=data,
        #         proxies=proxies,
        #     ).content
        # )
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
        return company_base_content, company_info_data, company_jobdam

    print(
        "---------------------------------KREDITJOB----------------------------------------"
    )
    company = process_name(company)
    search_url = f"https://www.kreditjob.com/api/search/autocomplete"
    search_response = json.loads(
        requests.get(
            search_url,
            params=[("q", company), ("index", 0), ("size", 5)],
            proxies=proxies,
        ).content
    )
    search_response = search_response.get("docs")
    for search_company in search_response:
        try:
            CMPN_NM = search_company["CMPN_NM"]
            WKP_ADRS = search_company["WKP_ADRS"]
            PK_NM_HASH = search_company["PK_NM_HASH"]

            try:
                k = KreditJob.objects.get(company_pk=PK_NM_HASH)
                now = timezone.now()
                if now < (k.updated + timedelta(days=7)):
                    print(CMPN_NM, "7일 지나지 않음, skip")
                    continue
                (
                    company_base_content,
                    company_info_data,
                    company_jobdam,
                ) = get_company_content(PK_NM_HASH)
                k.name = process_name(CMPN_NM)
                k.address = WKP_ADRS
                k.company_base_content = company_base_content
                k.company_info_data = company_info_data
                k.company_jobdam = company_jobdam
                k.save()
            except KreditJob.DoesNotExist:
                _address = WKP_ADRS.split(" ")
                if len(_address) >= 2:
                    _address[0] = _address[0].replace("광역시", "")
                    _address[0] = _address[0].replace(",", "")
                    _address = f"{_address[0]} {_address[1]}"
                else:
                    _address = WKP_ADRS
                (
                    company_base_content,
                    company_info_data,
                    company_jobdam,
                ) = get_company_content(PK_NM_HASH)
                KreditJob.objects.create(
                    name=process_name(CMPN_NM),
                    address=WKP_ADRS,
                    search_address=_address,
                    company_pk=PK_NM_HASH,
                    company_base_content=company_base_content,
                    company_info_data=company_info_data,
                    company_jobdam=company_jobdam,
                )
                print("kreditjob", CMPN_NM, "저장")
        except Exception as e:
            print("크레딧잡 에러")
            print(traceback.print_exc())
