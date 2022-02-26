from bs4 import BeautifulSoup
import requests
from proxy import proxies
import re


def get_jobkorea_search(stext):
    # 검색어
    # stext = "stext=django"
    # 지역
    local = "local=B000%2CI010"
    # 경력 1: 신입 2: 경력 3: 신입, 경력
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
        url = f"https://www.jobkorea.co.kr/Search/?stext={stext}&{local}&{careerType}&{careerMin}&{careerMax}&{edu}&{Ord}&Page_No={str(Page_No)}"
        resq = requests.get(
            url,
            # proxies=proxies
        )

        soup = BeautifulSoup(resq.content, "lxml")
        search_list = soup.find("div", class_="recruit-info")
        search_list = soup.find("div", class_="list-default")
        try:
            search_list = search_list.find_all("li", {"class": "list-post"})
            Page_No += 1
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
            option = company.find_all("span")
            exp = option[0].text
            edu = option[1].text
            job_type = option[3].text
            location = option[4].text
            if location:
                _location = location.split(" ")
                if len(_location) >= 2:
                    location = f"{_location[0]} {_location[1]}"
            date = option[5].text
            data = {
                "name": name,
                "title": title,
                "url": url,
                "career": exp,
                "education": edu,
                "employment_type": job_type,
                "work_place": location,
                "deadlines": date,
            }
            return_list.append(data)
        if Page_No == 1:
            break
    return return_list
