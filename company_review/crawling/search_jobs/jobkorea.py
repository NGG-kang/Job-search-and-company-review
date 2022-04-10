from bs4 import BeautifulSoup
import requests
import os
import sys
import django
from pathlib import Path
from fake_headers import Headers

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(os.path.dirname(BASE_DIR))
from proxy import proxies
import re


def get_jobkorea_search(stext):
    # 검색어
    # stext = "stext=django"
    # 지역
    local = "local=B000%2CI010"
    # 경력type 1: 신입 2: 경력 3: 신입, 경력
    careerType = "careerType=1"
    careerMin = "careerMin=1"
    careerMax = "careerMax=3"
    Page_No = 1
    if careerType == "careerType=1":
        careerMin = ""
        careerMax = ""

    # 학력 0: 무관
    edu = "edu=0"
    # 정렬 RegDtDesc: 최근등록
    Ord = "Ord=RegDtDesc"
    return_list = []
    while True:
        if Page_No == 3:
            return return_list
        headers = Headers(os="mac", headers=True).generate()
        url = f"https://www.jobkorea.co.kr/Search/?stext={stext}&{local}&{careerType}&{careerMin}&{careerMax}&{Ord}&Page_No={str(Page_No)}"
        print(url)
        resq = requests.get(url, headers=headers, timeout=5)

        soup = BeautifulSoup(resq.content, "lxml")
        search_list = soup.find("div", class_="recruit-info")
        search_list = soup.find("div", class_="list-default")
        try:
            search_list = search_list.find_all("li", {"class": "list-post"})
        except AttributeError:
            return return_list
        for company in search_list:
            # 기업 이름
            company_nm = company.find("div", {"class": "post-list-corp"})
            company_nm = company_nm.find("a")
            url = f'https://www.jobkorea.co.kr/{company_nm["href"]}'
            name = company_nm["title"]
            name = re.sub(r"\([^)]*\)", "", name)
            name = re.sub(r"[^a-zA-Z0-9가-힣]", "", name)
            # 제목
            post_list_info = company.find("div", {"class": "post-list-info"})
            title = post_list_info.find("a")["title"]
            # 지원옵션
            option = company.find("p", class_="option")
            exp = option.find("span", class_="exp").text
            edu = (lambda a: a.text if a else "None")(option.find("span", class_="edu"))
            location = option.find("span", class_="loc long").text
            deadlines = option.find("span", class_="date").text
            options = company.find_all("span")
            job_type = "None"
            for opt in options:
                if "class" not in opt:
                    job_type = opt.text

            if location:
                _location = location.split(" ")
                if len(_location) >= 2:
                    location = f"{_location[0]} {_location[1]}"
            data = {
                "site": "jobkorea",
                "name": name,
                "title": title,
                "url": url,
                "career": exp,
                "education": edu,
                "employment_type": job_type,
                "work_place": location,
                "deadlines": deadlines,
            }
            return_list.append(data)
        Page_No += 1


# print(get_jobkorea_search("java"))
