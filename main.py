import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from flask_cors import CORS
import db

app = Flask(__name__)
CORS(app)

@app.route('/posts/<community>')
def get_posts(community):
    conn = db.postgresql_connect()
    if not conn:
        return jsonify({"error": "데이터베이스 연결 실패"}), 500
    db_posts = db.postgresql_select(conn, community)
    conn.close()
    
    if db_posts is None:
        return jsonify({"error": "게시물을 불러오는 중 오류가 발생했습니다."}), 500
    return jsonify({"posts": db_posts})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
