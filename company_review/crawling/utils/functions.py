from django.core.cache import cache


def is_search_already(company_name):
    is_search_already = cache.get(company_name)
    if not is_search_already:
        cache.set(company_name, 604800)
        return False
    return True
