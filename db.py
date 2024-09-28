import psycopg2
import os
from dotenv import load_dotenv

def postgresql_connect():
    load_dotenv()
    try:
        connection = psycopg2.connect(
            dbname=os.environ.get("POSTGRES_DB"),
            user=os.environ.get("POSTGRES_USER"),
            password=os.environ.get("POSTGRES_PASSWORD"),
            host=os.environ.get("POSTGRES_HOST"),
            port=os.environ.get("POSTGRES_PORT")
        )
        print("PostgreSQL 데이터베이스에 연결되었습니다.")
        return connection
    except Exception as e:
        print(f"데이터베이스 연결 오류: {e}")
        return None

def postgresql_insert(connection, post, community):
    try:
        cursor = connection.cursor()
        sql = f"INSERT INTO {community}_posts VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (post['post_num'], post['post_title'], post['post_link'], post['post_look_count'], post['post_likes_count']))
        connection.commit()
        cursor.close()
        print("데이터베이스에 데이터가 저장되었습니다.")
    except Exception as e:
        print(f"데이터베이스 저장 오류: {e}")

def postgresql_select(connection, community):
    try:
        cursor = connection.cursor()
        sql = f"SELECT * FROM {community}_posts ORDER BY created_at DESC"
        cursor.execute(sql)
        posts = cursor.fetchall()
        cursor.close()
        return posts
    except Exception as e:
        print(f"데이터베이스 조회 오류: {e}")
        return []
