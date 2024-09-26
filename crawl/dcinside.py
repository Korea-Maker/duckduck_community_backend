import requests
from bs4 import BeautifulSoup
import time
import re
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db

# [디시인사이드]
# 실시간 베스트
# ㅇㅎ빼고
# 조회수 8000 이상 20,000 이하
# 추천 80 이상 200이하

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

def dc_best_crawl():

    community = 'dcinside'
    # 데이터베이스 연결
    connection = db.postgresql_connect()
    if not connection:
        print("데이터베이스에 연결할 수 없습니다. 크롤링을 중단합니다.")
        return

    try:
        for page in range(1, 10):
            url = f'https://gall.dcinside.com/board/lists/?id=dcbest&page={page}&_dcbest=1'
            print(f"크롤링 중: {url}")
            response = requests.get(url, headers={"User-Agent": USER_AGENT})

            # 응답 상태 코드 확인
            if response.status_code != 200:
                print(f"페이지 {page}을 가져오는 데 실패했습니다. 상태 코드: {response.status_code}")
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            posts = soup.select('tbody.listwrap2 .ub-content.us-post.thum')

            if not posts:
                print(f"페이지 {page}에 게시글이 없습니다.")
                continue

            for post in posts:
                try:
                    post_title_re = post.select_one('.gall_tit.ub-word').get_text().strip().replace('\n', '')
                    if "ㅇㅎ" in post_title_re or "야갤" in post_title_re:
                        continue

                    post_look_count = post.select_one('.gall_count').get_text().strip()
                    post_likes_count = post.select_one('.gall_recommend').get_text().strip()

                    if 8000 <= int(post_look_count) <= 20000 and 80 <= int(post_likes_count) <= 200:
                        continue

                    post_num = post.select_one('.gall_num').get_text().strip()
                    post_link = post.select_one('.gall_tit.ub-word a').get('href')

                    if not post_link.startswith('http'):
                        post_link = f"https://gall.dcinside.com{post_link}"

                    post_title = re.sub(r'^$$[^$$]+\]\s*|$$\d+$$$', '', post_title_re).strip()

                    post_data = {
                        'post_num': int(post_num),  # 숫자로 변환
                        'post_title': post_title,
                        'post_link': post_link,
                        'post_look_count': int(post_look_count.replace(',', '')),
                        'post_likes_count': int(post_likes_count.replace(',', ''))
                    }

                    db.postgresql_insert(connection, post_data, community)

                    print(f"게시글 저장: {post_data['post_num']} - {post_data['post_title']}")

                except Exception as e:
                    print(f"게시글 처리 중 오류 발생: {e}")

                # 너무 빠르게 요청하지 않도록 잠시 대기
                time.sleep(0.5)  # 2초 대신 1초로 조정 (필요 시 다시 2초로 변경)
    finally:
        # 크롤링 종료 후 데이터베이스 연결 종료
        connection.close()
        print("데이터베이스 연결을 종료했습니다.")

if __name__ == "__main__":
    dc_best_crawl()
