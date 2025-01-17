import mysql.connector
from mysql.connector import Error

class DBManager:
    def __init__(self):
        # MySQL 연결 설정
        self.conn = mysql.connector.connect(
            host='10.0.66.11',
            user='dbqls',  # MySQL 사용자명
            password='1234',  # MySQL 비밀번호
            database='busniess_cards'  # 사용하려는 DB 이름
        )
        self.cursor = self.conn.cursor()

    def get_all_posts(self):
        query = "SELECT * FROM business_cards"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    def get_post_by_id(self, post_id):
        query = "SELECT * FROM business_cards WHERE id = %s"
        self.cursor.execute(query, (post_id,))
        result = self.cursor.fetchone()
        return result

    def insert_post(self, title, content, filename=None):
        query = "INSERT INTO business_cards (title, content, file_name) VALUES (%s, %s, %s)"
        self.cursor.execute(query, (title, content, filename))
        self.conn.commit()
        return True

    def update_post(self, post_id, title, content, filename=None):
        query = "UPDATE business_cards SET title = %s, content = %s, file_name = %s WHERE id = %s"
        self.cursor.execute(query, (title, content, filename, post_id))
        self.conn.commit()
        return True

    def delete_post(self, post_id):
        query = "DELETE FROM business_cards WHERE id = %s"
        self.cursor.execute(query, (post_id,))
        self.conn.commit()
        return True

    def __del__(self):
        try:
            if self.cursor:
                self.cursor.close()
        except AttributeError:
            pass  # cursor가 없다면 무시
        finally:
            if self.conn:
                self.conn.close()
