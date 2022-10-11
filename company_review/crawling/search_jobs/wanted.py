
import requests
from bs4 import BeautifulSoup
import json
from fake_headers import Headers
from celeries.tasks import get_jobplanet_info, get_kreditjob_info, get_saramin_info
from django.core.cache import cache
from config.utils import process_name


def get_wanted_search(wanted):
    if not wanted:
        return [], 0
    tag_type_ids, skill_tags = list(wanted.values())
    wanted_jobs_res = requests.get(f"https://www.wanted.co.kr/api/v4/jobs?country=kr&job_sort=job.latest_order&tag_type_ids={tag_type_ids}&skill_tags={skill_tags}&locations=seoul.all&locations=gyeonggi.all&limit=100").json()
    # print(wanted_jobs_res)
    jobs = wanted_jobs_res['data']
    return_list = list()
    for job in jobs:
        if not job['status'] == 'active':
            continue
        company_name = job['company']['name']
        company_name = process_name(company_name)
        deadlines = job['due_time']
        address = job['address']['location']
        title = job['position']
        gongo_pk = job['id']
        gongo_url = f"https://www.wanted.co.kr/wd/{gongo_pk}"

        # headers = {
        #     'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        #     "accept": "text/html",
        #     "authority": "www.wanted.co.kr",
        #     "method": "GET",
        #     "path": f"/wd/{gongo_pk}", 
        #     "scheme": "https"
        # }
        # gongo_res = requests.get(gongo_url, headers=headers)
        # soup = BeautifulSoup(gongo_res.content, 'lxml')
        # script = soup.find("script", {"id": "__NEXT_DATA__"}).text

        # with open('test2.json', 'w', encoding="utf-8") as f:
        #     json.dump(script, f, indent=4, ensure_ascii=False)
        
        # created = json.loads(script)
        # cretaed = created['props']['pageProps']['head']['gongo_pk']['confirm_time']
        data = {
            "site": "wanted",
            "name": company_name,
            "pk": gongo_pk,
            "count": 0,
            "title": title,
            "url": gongo_url,
            "career": "-",
            "education": "-",
            "employment_type": "-",
            "work_place": address,
            "deadlines": deadlines,
            "created": "-"
        }
        return_list.append(data)

    is_search_already = cache.get(company_name)
    if not is_search_already:
        cache.set(company_name, 86400, 86400)
        get_saramin_info.apply_async(kwargs={'name': company_name, 'update': True}, queue='saramin', priority=2)
        get_jobplanet_info.apply_async(kwargs={'name': company_name, 'update': True}, queue='joplanet', priority=2)
        get_kreditjob_info.apply_async(kwargs={'name': company_name, 'update': True}, queue='kreditjob', priority=2)
    return return_list, len(return_list)
        
        
