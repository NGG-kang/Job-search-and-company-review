from celery import shared_task
from celeries.get_compnay_info import (
    get_kreditjob_company,
    get_saramin_company,
    get_jobplanet_company,
)


@shared_task
def get_company_info(name, update=False):
    print("시작: " + name)
    print("---------------------------------잡플래닛 시작: " + name + "----------------------------------------")
    get_jobplanet_company(name, update)
    print("---------------------------------사람인 시작: " + name + "----------------------------------------")
    get_saramin_company(name, update)
    print("---------------------------------크래딧잡 시작: " + name + "----------------------------------------")
    get_kreditjob_company(name, update)