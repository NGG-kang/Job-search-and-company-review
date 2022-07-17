import re


def process_name(name):
    name = re.sub(r"\([^)]*\)", "", name)
    name = re.sub(r"（[^)]*）", "", name)

    name = re.sub(r"[^a-zA-Z0-9가-힣]", "", name)
    name = re.sub(r"주식회사", "", name)
    return name.strip()

def process_address(address):
    _address = address.split(" ")
    if len(_address) >= 2:
        _address[0] = _address[0].replace("광역시", "")
        _address[0] = _address[0].replace("특별시", "")
        _address[0] = _address[0].replace(",", "")
        _address = f"{_address[0]} {_address[1]}"
        return _address
    return address