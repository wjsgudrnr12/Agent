import json
import requests
from bs4 import BeautifulSoup


def google_searching(keyword: str, limit=5):
    google_search_url = 'https://www.google.com/search'

    params = {'q': keyword, 'tbm': 'nws', 'num': limit}

    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
    }

    res = requests.get(google_search_url, params=params, headers=headers)

    soup = BeautifulSoup(res.content, 'html.parser')

    news_results = []
    for el in soup.select("div.SoaBEf"):
        news_results.append(
            {
                "link": el.find("a")["href"],
                "title": el.select_one("div.MBeuO").get_text(),
                "snippet": el.select_one(".GI74Re").get_text()
            }
        )

    return news_results

def google_searching_from_links(links):
    details = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
    }

    for link in links:
        res = requests.get(link, headers=headers)
        soup = BeautifulSoup(res.content, 'html.parser')
        
        # 페이지 타이틀 추출
        page_title = soup.title.text if soup.title else 'No Title Found'
        
        # 페이지 본문 추출
        body_text = ' '.join([p.text.strip() for p in soup.find_all('p')])
        
        details.append({
            'link': link,
            'page_title': page_title,
            'body_text': body_text  # 본문 추가
        })
    
    return details


def extract_google_search(keyword: str, limit=5):

    searching_results = google_searching(keyword, limit)

    # 사용 예제
    links = [result['link'] for result in searching_results]

    additional_details = google_searching_from_links(links)

    return additional_details
    # 결과 출력
    for detail in additional_details:
        print(f"\n{detail}")

