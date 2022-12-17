import requests
from bs4 import BeautifulSoup

URL = 'https://ap.ece.moe.edu.tw/webecems/pubSearch.aspx'
TARGET_CITY = "09"
TARGET_AREA = "428"


def get_data(text, keyword):
    keyword += '|'
    start_idx = text.index(keyword) + len(keyword)
    end_idx = text.index('|', start_idx)
    return text[start_idx: end_idx]


def in_session(s):
    # Copy headers from edge
    s.headers.update({"Accept-Encoding": "gzip, deflate, br",
                      "Accept-Language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7,mt;q=0.6",
                      "Cache-Control": "no-cache",
                      "Connection": "keep-alive",
                      "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                      "Host": "ap.ece.moe.edu.tw",
                      "Origin": "https://ap.ece.moe.edu.tw",
                      "Referer": "https://ap.ece.moe.edu.tw/webecems/pubSearch.aspx",
                      "sec-ch-ua": '\"Not?A_Brand";v="8", "Chromium";v="108", "Microsoft Edge";v="108\"',
                      "sec-ch-ua-mobile": "?0",
                      "sec-ch-ua-platform": "Windows",
                      "Sec-Fetch-Dest": "empty",
                      "Sec-Fetch-Mode": "cors",
                      "Sec-Fetch-Site": "same-origin",
                      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.46",
                      "X-MicrosoftAjax": "Delta=true",
                      "X-Requested-With": "XMLHttpRequest",
                      })

    # Get the first lookup page
    response = s.get(URL)
    with open("get.html", "w", encoding="utf8") as f:
        f.write(response.text)

    soup = BeautifulSoup(response.text, 'html.parser')
    dic = {
        "ScriptManager1": "UpdatePanel1|ddlCityS",
        "ddlKey": "",
        "txtKeyNameS": "",
        "ddlCityS": TARGET_CITY,
        "ddlAreaS": "",
        "__EVENTTARGET": "ddlCityS",
        "__LASTFOCUS": "",
        "__ASYNCPOST": "true",
        "__EVENTARGUMENT": soup.find(id="__EVENTARGUMENT")['value'],
        "__VIEWSTATE": soup.find(id="__VIEWSTATE")['value'],
        "__EVENTVALIDATION": soup.find(id="__EVENTVALIDATION")['value'],
        "__VIEWSTATEGENERATOR": soup.find(id="__VIEWSTATEGENERATOR")['value'],
        "__VIEWSTATEENCRYPTED": soup.find(id="__VIEWSTATEENCRYPTED")['value'],
    }

    # Select city
    response = s.post(URL, data=dic)
    with open("select_city.html", "w", encoding="utf8") as f:
        f.write(response.text)
    dic.update({"__EVENTVALIDATION": get_data(response.text, '__EVENTVALIDATION'),
                "__VIEWSTATE": get_data(response.text, '__VIEWSTATE'),
                "ScriptManager1": "UpdatePanel1|btnSearch",
                "ddlAreaS": TARGET_AREA,
                "btnSearch": "搜尋",
                "__EVENTTARGET": "",
                })
    # Search
    response = s.post(URL, data=dic)
    with open("result.html", "w", encoding="utf8") as f:
        f.write(response.text)

    # Save verification code
    soup = BeautifulSoup(response.text, 'html.parser')
    dic.update({"__EVENTVALIDATION": get_data(response.text, '__EVENTVALIDATION'),
                '__VIEWSTATE': get_data(response.text, '__VIEWSTATE'), })
    idx = 0
    while True:
        _id = f'GridView1_imgValidateCode_{idx}'
        idx += 1
        img = soup.find(id=_id)
        if img:
            url = 'https://ap.ece.moe.edu.tw/webecems/' + img['src']
            reponse = s.get(url)
            with open(f'{_id}.png', "wb") as f:
                f.write(reponse.content)
        else:
            break

    PREVFIX = 'popwin=window.open(\'./'
    POSTFIX = '&'
    idx = 0
    while True:
        _id = f'GridView1_divChgList_{idx}'
        idx += 1
        div = soup.find(id=_id)
        if div:
            code = div.find('a')['onclick']
            start = code.index(PREVFIX) + len(PREVFIX)
            end = code.index(POSTFIX)
            _url = code[start:end]
            _url = 'https://ap.ece.moe.edu.tw/webecems/' + _url + '&v=verification_code'
        else:
            break


def main():
    with requests.Session() as s:
        in_session(s)


if __name__ == '__main__':
    main()
