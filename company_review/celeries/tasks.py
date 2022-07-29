from celery import shared_task
import traceback
from celeries.get_compnay_info import (
    get_kreditjob_company,
    get_saramin_company,
    get_jobplanet_company,
)


@shared_task
def get_saramin_info(name, update=False):
    get_saramin_company(name, update)


@shared_task
def get_jobplanet_info(name, update=False):
    get_jobplanet_company(name, update)


@shared_task
def get_kreditjob_info(name, update=False):
    try:
        get_kreditjob_company(name, update)
    except:
        print(traceback.print_exc())