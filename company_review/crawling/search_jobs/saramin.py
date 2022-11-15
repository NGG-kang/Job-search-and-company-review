from bs4 import BeautifulSoup
import requests
import re
from proxy import proxies
import traceback
from celeries.tasks import get_jobplanet_info, get_kreditjob_info, get_saramin_info
from config.utils import process_name
from django.core.cache import cache
from django.conf import settings
from fake_headers import Headers


def get_saramin_search(stext):
    # name = "django"
    url = "https://www.saramin.co.kr/zf_user/jobs/list/domestic?"
    # 지역 서울, 경기
    loc = "loc_mcd=101000%2C102000"
    # 검색단어
    searchword = f"searchword={stext}"
    # 정렬 관련도순: RL, 수정일순: MD, 최근등록순: RD, 마감임박순: EA, 지원자순: AD
    sort = "sort=RD"
    # 페이지
    page = 1
    # 1: 신입 2: 경력
    exp_cd = "exp_cd=2"
    # 년도 최소, 신입은 없음
    exp_min = "exp_min=1"
    # 년도 맥시멈
    exp_max = "exp_max=10"
    return_list = []
    if exp_cd == "exp_cd=1":
        exp_min = ""
        exp_max = ""
        edu_none = ""
    else:
        edu_none = "edu_none=y"
    while True:
        url = f"https://www.saramin.co.kr/zf_user/jobs/list/domestic?{loc}&{searchword}&{sort}&page={str(page)}&{exp_cd}&{exp_min}&{exp_max}"
        print(url)
        headers = Headers(os="mac", headers=True).generate()
        resq = requests.get(
            url,
            headers=headers,
            # proxies=proxies
        )
        soup = BeautifulSoup(resq.content, "lxml")
        search_list = soup.find("div", class_="list_body")
        search_list = search_list.find_all("div", {"id": re.compile(r"rec-.*")})
        if not search_list:
            return return_list
        if page == 3:
            break
        for company in search_list:
            rec_idx = company['id']
            # 기업 이름
            company_nm = company.find("div", {"class": "col company_nm"})
            company_name = company_nm.find("a")["title"]
            company_name = process_name(company_name)
            company_pk = company_nm.find("button")["csn"]
            company_gongos = cache.get(f"{stext}:{company_name}")
            if company_gongos: 
                if rec_idx not in company_gongos:
                    company_gongos.append(rec_idx)
            else:
                company_gongos = [rec_idx]
            cache.set(f"{stext}:{company_name}", company_gongos, 2678400)

            
            # 제목
            notification_info = company.find("div", {"class": "col notification_info"})
            notification_info = notification_info.find("a")
            title = notification_info["title"]
            url = f"https://www.saramin.co.kr{notification_info['href']}"
            # 지원자격
            recruit_condition = company.find("div", {"class": "col recruit_condition"})
            career = recruit_condition.find("p", class_="career").text
            education = recruit_condition.find("p", class_="education").text
            # 근무조건
            company_info = company.find("div", {"class": "col company_info"})
            try:
                employment_type = company_info.find("p", class_="employment_type").text
            except:
                employment_type = "없음"
            work_place = company_info.find("p", class_="work_place").text
            if work_place:
                _work_place = work_place.split(" ")
                if len(_work_place) >= 2:
                    work_place = f"{_work_place[0]} {_work_place[1]}"
            # 마감일, 등록일
            support_info = company.find("div", {"class": "col support_info"})
            deadlines = support_info.find("p", class_="deadlines").text
            data = {
                "site": "saramin",
                "name": company_name,
                "pk": company_pk,
                "count": len(company_gongos),
                "title": title,
                "url": url,
                "career": career,
                "education": education,
                "employment_type": employment_type,
                "work_place": work_place,
                "deadlines": deadlines,
            }
            return_list.append(data)
            is_search_already = cache.get(company_name)
            if not is_search_already:
                cache.set(company_name, 86400, 86400)
                get_saramin_info.apply_async(kwargs={'name': company_name, 'update': True}, queue='saramin', priority=2)
                get_jobplanet_info.apply_async(kwargs={'name': company_name, 'update': True}, queue='joplanet', priority=2)
                get_kreditjob_info.apply_async(kwargs={'name': company_name, 'update': True}, queue='kreditjob', priority=2)
        page += 1
        print(page)
        
        return return_list, len(return_list)
