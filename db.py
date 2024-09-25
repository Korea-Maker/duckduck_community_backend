import os
import logging
from psycopg2 import pool, extras
from dotenv import load_dotenv

class Database:
    def __init__(self):
        load_dotenv()
        try:
            self.pool = psycopg2.pool.SimpleConnectionPool(
                1,  # 최소 연결 수
                20,  # 최대 연결 수
                dbname=os.environ.get("POSTGRES_DB"),
                user=os.environ.get("POSTGRES_USER"),
                password=os.environ.get("POSTGRES_PASSWORD"),
                host=os.environ.get("POSTGRES_HOST"),
                port=os.environ.get("POSTGRES_PORT"),
                cursor_factory=extras.RealDictCursor  # 결과를 딕셔너리 형태로 반환
            )
            if self.pool:
                logging.info("PostgreSQL 연결 풀 생성됨.")
        except Exception as e:
            logging.error(f"데이터베이스 연결 풀 오류: {e}")

    def connect(self):
        try:
            conn = self.pool.getconn()
            if conn:
                logging.info("데이터베이스 연결 가져옴.")
                return conn
        except Exception as e:
            logging.error(f"연결 가져오기 오류: {e}")
        return None

    def disconnect(self, conn):
        try:
            self.pool.putconn(conn)
            logging.info("데이터베이스 연결 반환됨.")
        except Exception as e:
            logging.error(f"연결 반환 오류: {e}")

    def close_pool(self):
        try:
            self.pool.closeall()
            logging.info("모든 데이터베이스 연결 종료됨.")
        except Exception as e:
            logging.error(f"연결 종료 오류: {e}")

    def insert_post(self, post, community):
        conn = self.connect()
        if not conn:
            return False
        try:
            with conn.cursor() as cursor:
                sql = f"INSERT INTO {community}_posts (post_num, post_title, post_link, post_look_count, post_likes_count) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (
                    post['post_num'],
                    post['post_title'],
                    post['post_link'],
                    post['post_look_count'],
                    post['post_likes_count']
                ))
            conn.commit()
            logging.info("데이터베이스에 데이터가 저장되었습니다.")
            return True
        except Exception as e:
            logging.error(f"데이터베이스 저장 오류: {e}")
            return False
        finally:
            self.disconnect(conn)

    def select_posts(self, community):
        conn = self.connect()
        if not conn:
            return []
        try:
            with conn.cursor() as cursor:
                sql = f"SELECT * FROM {community}_posts"
                cursor.execute(sql)
                posts = cursor.fetchall()
                logging.info("데이터베이스에서 데이터 조회 완료.")
                return posts
        except Exception as e:
            logging.error(f"데이터베이스 조회 오류: {e}")
            return []
        finally:
            self.disconnect(conn)

