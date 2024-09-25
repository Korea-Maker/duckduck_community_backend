from flask import Flask, jsonify
from flask_cors import CORS
import logging
from db import Database

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# Flask 애플리케이션 초기화
app = Flask(__name__)
CORS(app)

# 데이터베이스 인스턴스 생성
database = Database()

@app.route('/posts/<community>', methods=['GET'])
def get_posts(community):
    db_posts = database.select_posts(community)
    if db_posts is None:
        return jsonify({"error": "게시물을 불러오는 중 오류가 발생했습니다."}), 500
    return jsonify({"posts": db_posts}), 200

if __name__ == "__main__":
    try:
        app.run()  # 호스트와 포트를 설정
    except Exception as e:
        logging.error(f"Flask 서버 실행 오류: {e}")
    finally:
        database.close_pool()  # 서버 종료 시 연결 풀 종료
