import requests
from bs4 import BeautifulSoup
import time
import re
import db

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
                    post_num = post.select_one('.gall_num').get_text().strip()
                    post_title_re = post.select_one('.gall_tit.ub-word').get_text().strip().replace('\n', '')
                    post_link = post.select_one('.gall_tit.ub-word a').get('href')

                    # link가 절대 경로가 아닌 경우 절대 경로로 변환
                    if not post_link.startswith('http'):
                        post_link = f"https://gall.dcinside.com{post_link}"

                    # 정규 표현식을 사용하여 제목 클린업
                    post_title = re.sub(r'\$\$[가-힣]{2}\s*\$\$', '', post_title_re).strip()

                    post_look_count = post.select_one('.gall_count').get_text().strip()
                    post_likes_count = post.select_one('.gall_recommend').get_text().strip()

                    # 게시글 데이터를 딕셔너리로 구성
                    post_data = {
                        'post_num': int(post_num),  # 숫자로 변환
                        'post_title': post_title,
                        'post_link': post_link,
                        'post_look_count': int(post_look_count.replace(',', '')),
                        'post_likes_count': int(post_likes_count.replace(',', ''))
                    }

                    # 데이터베이스에 삽입
                    db.postgresql_insert(connection, post_data, community)

                    print(f"게시글 저장: {post_data['post_num']} - {post_data['post_title']}")

                except Exception as e:
                    print(f"게시글 처리 중 오류 발생: {e}")

                # 너무 빠르게 요청하지 않도록 잠시 대기
                time.sleep(1)  # 2초 대신 1초로 조정 (필요 시 다시 2초로 변경)
    finally:
        # 크롤링 종료 후 데이터베이스 연결 종료
        connection.close()
        print("데이터베이스 연결을 종료했습니다.")

if __name__ == "__main__":
    dc_best_crawl()
