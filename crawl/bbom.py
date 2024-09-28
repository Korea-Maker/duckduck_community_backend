from urllib.parse import urlparse, parse_qs
import requests
from bs4 import BeautifulSoup
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

def crawl(url):
    community = 'bb'
    # 데이터베이스 연결
    connection = db.postgresql_connect()
    if not connection:
        print("데이터베이스에 연결할 수 없습니다. 크롤링을 중단합니다.")
        return

    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')
        datas = soup.select('#__next > div > main > div > div > ul > li')
        for data in datas:
            try:
                like_count = data.select_one('div > div > p > button > span:nth-child(2)').get_text().strip()
                if int(like_count) <= 100:
                    continue
                post_link = data.select_one('div > div > p > a').get('href').split('#')[0]
                title = data.select_one('div + strong').get_text().strip()
                if not post_link.startswith('http'):
                    post_link = f"https://m.bboom.naver.com{post_link}"

                parsed_url = urlparse(post_link)
                query_params = parse_qs(parsed_url.query)
                post_num = query_params.get('postNo', [None])[0]
                post_look_count = 0

                post_data = {
                    'post_num': int(post_num),  # 숫자로 변환
                    'post_title': title,
                    'post_link': post_link,
                    'post_look_count': post_look_count,
                    'post_likes_count': int(like_count.replace(',', ''))
                }
                db.postgresql_insert(connection, post_data, community)
            except Exception as e:
                print(f"게시글 저장 오류: {e}")
            time.sleep(0.5)
    finally:
        # 크롤링 종료 후 데이터베이스 연결 종료
        connection.close()
        print("데이터베이스 연결을 종료했습니다.")

if __name__ == "__main__":
    crawl('https://m.bboom.naver.com/')
