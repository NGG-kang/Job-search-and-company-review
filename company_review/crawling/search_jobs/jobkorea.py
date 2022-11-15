from bs4 import BeautifulSoup
import requests
from fake_headers import Headers
from traceback import print_exc
from celeries.tasks import get_kreditjob_info, get_jobplanet_info, get_saramin_info
from config.utils import process_name
from django.core.cache import cache


def get_jobkorea_search(stext):
    # 검색어
    # stext = "stext=django"
    # 지역 서울, 경기
    local = "local=B000%2CI010"
    # 경력type 1: 신입 2: 경력 3: 신입, 경력
    careerType = "careerType=3"
    careerMin = "careerMin=1"
    careerMax = "careerMax=10"
    Page_No = 1
    if careerType == "careerType=1":
        careerMin = ""
        careerMax = ""

    # 학력 0: 무관
    edu = "edu=0"
    # 정렬 RegDtDesc: 최근등록
    Ord = "Ord=RegDtDesc"
    return_list = []
    url = f"https://www.jobkorea.co.kr/Search/?stext={stext}&{local}&{careerType}&{careerMin}&{careerMax}&{Ord}"
    try:
        while True:
            if Page_No == 3:
                return return_list, len(return_list)
            headers = Headers(os="mac", headers=True).generate()
            url_and_page = f"{url}&Page_No={str(Page_No)}"
            print(url_and_page)
            resq = requests.get(url_and_page, headers=headers, timeout=5)

            soup = BeautifulSoup(resq.content, "lxml")
            search_list = soup.find("div", class_="recruit-info")
            search_list = soup.find("div", class_="list-default")
            # 페이지에 공고가 없는경우
            try:
                search_list = search_list.find_all("li", {"class": "list-post"})
            except AttributeError:
                return return_list, len(return_list)
            for company in search_list:
                # 기업 이름
                company_nm = company.find("div", {"class": "post-list-corp"})
                company_nm = company_nm.find("a")
                url = f'https://www.jobkorea.co.kr/{company_nm["href"]}'
                name = company_nm["title"]
                name = process_name(name)
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
                is_search_already = cache.get(name)
                if not is_search_already:
                    cache.set(name, 86400)
                    get_saramin_info.apply_async(kwargs={'name': name, 'update': True}, queue='saramin', priority=2)
                    get_jobplanet_info.apply_async(kwargs={'name': name, 'update': True}, queue='joplanet', priority=2)
                    get_kreditjob_info.apply_async(kwargs={'name': name, 'update': True}, queue='kreditjob', priority=2)
            Page_No += 1
    except:
        print(print_exc())


# print(get_jobkorea_search("java"))
