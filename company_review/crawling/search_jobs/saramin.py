from bs4 import BeautifulSoup
import requests
import re
from proxy import proxies


def get_saramin_search(name):
    # name = "django"
    url = "https://www.saramin.co.kr/zf_user/jobs/list/domestic?"
    # 지역
    loc = "loc_mcd=101000%2C102000"
    # 검색단어
    searchword = "searchword=django"
    # 정렬 관련도순: RL, 수정일순: MD, 최근등록순: RD, 마감임박순: EA, 지원자순: AD
    sort = "sort=RD"
    # 페이지
    page = 1
    # 1: 신입 2: 경력
    exp_cd = "exp_cd=1"
    # 년도 최소, 신입은 없음
    exp_min = "exp_min=1"
    # 년도 맥시멈
    exp_max = "exp_max=1"
    return_list = []
    if exp_cd == "exp_cd=1":
        exp_min = ""
        exp_max = ""
        edu_none = ""
    else:
        edu_none = "edu_none=y"
    while True:
        resq = requests.get(
            f"https://www.saramin.co.kr/zf_user/jobs/list/domestic?{loc}&{searchword}&{sort}&page={str(page)}&{edu_none}&{exp_cd}&{exp_min}&{exp_max}",
            proxies=proxies,
        )
        soup = BeautifulSoup(resq.content, "lxml")
        search_list = soup.find("div", class_="list_body")
        search_list = search_list.find_all("div", {"id": re.compile(r"rec-.*")})
        if not search_list:
            return return_list
        else:
            page += 1
        for company in search_list:
            # 기업 이름
            company_nm = company.find("div", {"class": "col company_nm"})
            company_nm = company_nm.find("a")
            company_url = company_nm["href"]
            name = company_nm["title"]
            name = re.sub(r"\([^)]*\)", "", name)
            name = re.sub(r"[^a-zA-Z0-9가-힣]", "", name)
            # 제목
            notification_info = company.find("div", {"class": "col notification_info"})
            notification_info = notification_info.find("a")
            title = notification_info["title"]
            url = f'https://www.saramin.co.kr{notification_info["href"]}'
            # 지원자격
            recruit_condition = company.find("div", {"class": "col recruit_condition"})
            career = recruit_condition.find("p", class_="career").text
            education = recruit_condition.find("p", class_="education").text
            # 근무조건
            company_info = company.find("div", {"class": "col company_info"})
            employment_type = company_info.find("p", class_="employment_type").text
            work_place = company_info.find("p", class_="work_place").text
            if work_place:
                _work_place = work_place.split(" ")
                if len(_work_place) >= 2:
                    work_place = f"{_work_place[0]} {_work_place[1]}"
            # 마감일, 등록일
            support_info = company.find("div", {"class": "col support_info"})
            deadlines = support_info.find("p", class_="deadlines").text
            data = {
                "name": name,
                "title": title,
                "url": url,
                "career": career,
                "education": education,
                "employment_type": employment_type,
                "work_place": work_place,
                "deadlines": deadlines,
            }
            return_list.append(data)
        if page == 1:
            break
        return return_list
