import mysql.connector
from mysql.connector import Error
import hashlib


class DBManager:
    def __init__(self):
        self.connection = None
        self.cursor = None


    # DB에 연결
    def connect(self):
        if self.connection and self.connection.is_connected():
            return
        try:
            self.connection = mysql.connector.connect(
                host='10.0.66.11',
                user='dbqls',
                password='1234',
                database='business_cards'
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
        except mysql.connector.Error as error:
            print(f"데이터베이스 연결 실패: {error}")
            self.cursor = None


    # 데이터베이스 연결 종료
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()


    # 비밀번호 암호화
    def hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    # 회원 가입
    def register_user(self, userid, password, email, username, phone, profile_picture):
        self.connect()
        try:
            # 중복 체크를 순차적으로 수행
            checks = [
                ('userid', userid, "아이디가 이미 존재합니다."),
                ('email', email, "이메일이 이미 존재합니다."),
                ('phone', phone, "핸드폰 번호가 이미 존재합니다.")
            ]
            
            for field, value, error_message in checks:
                if self.is_field_exists(field, value):
                    return False, error_message
            # 모든 중복 체크를 통과한 경우 회원 등록 진행
            hashed_password = self.hash_password(password)
            query = """
            INSERT INTO users (userid, password, email, username, phone, profile_picture)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (userid, hashed_password, email, username, phone, profile_picture)
            self.cursor.execute(query, values)
            self.connection.commit()
            return True, "회원가입이 완료되었습니다."
        except Error as e:
            return False, f"회원가입 실패: {e}"
        finally:
            self.disconnect()

    def is_field_exists(self, field, value):
        self.connect()
        try:
            query = f"SELECT 1 FROM users WHERE {field} = %s"
            self.cursor.execute(query, (value,))
            return self.cursor.fetchone() is not None
        except Error as e:
            print(f"{field} 중복 체크 중 오류 발생: {e}")
            return False
        finally:
            self.disconnect()


    # 로그인
    def login_user(self, userid, password):
        self.connect()
        try:
            # 사용자 정보 조회
            query = "SELECT * FROM users WHERE userid = %s"
            self.cursor.execute(query, (userid,))
            user = self.cursor.fetchone()

            if user:
                # 입력받은 비밀번호를 해시화
                input_hashed_password = hashlib.sha256(password.encode()).hexdigest()
                
                # 저장된 비밀번호와 비교
                if input_hashed_password == user['password']:
                    return True, "로그인 성공"
                else:
                    return False, "비밀번호가 일치하지 않습니다"
            else:
                return False, "사용자를 찾을 수 없습니다"
        except Exception as e:
            return False, f"로그인 중 오류 발생: {str(e)}"
        finally:
            self.disconnect()


    # 명함 추가
    def insert_post(self, user_id, name, company_name, department, position, phone, email, filename):
        self.connect()
        try:
            query = """
            INSERT INTO my_business_cards (user_id, name, company_name, department, position, phone, email, filename)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (user_id, name, company_name, department, position, phone, email, filename)
            self.cursor.execute(query, values)
            self.connection.commit()
            print("명함이 추가되었습니다.")
            return True
        except Error as e:
            print(f"명함 추가 실패: {e}")
            return False
        finally:
            self.disconnect()


    # 내명함 가져오기
    def get_all_posts_user(self, user_id):
        self.connect()
        try:
            query = """
            SELECT mb.*
            FROM my_business_cards mb
            JOIN users u ON mb.user_id = u.userid
            WHERE u.userid = %s
            """
            self.cursor.execute(query, (user_id,))
            posts = self.cursor.fetchall()
            return posts  
        except Exception as e:
            print(f"명함 조회 실패: {e}")
            return []
        finally:
            self.disconnect()



    # 모든 명함 가져오기
    def get_all_posts(self):
        self.connect()
        try:
            self.cursor.execute("SELECT * FROM business_cards")
            return self.cursor.fetchall()
        except Error as e:
            print(f"명함 가져오기 실패: {e}")
            return []
        finally:
            self.disconnect()


    # 특정 명함 가져오기
    def get_post_by_id(self, post_id):
        self.connect()
        try:
            query = "SELECT * FROM business_cards WHERE id = %s"
            self.cursor.execute(query, (post_id,))
            return self.cursor.fetchone()
        except Error as e:
            print(f"명함 조회 실패: {e}")
            return None
        finally:
            self.disconnect()

    # 명함 수정
    def update_post(self, post_id, name, company_name, department, phone, email, filename):
        self.connect()
        try:
            query = """
            UPDATE business_cards
            SET name = %s, company_name = %s, department = %s, phone = %s, email = %s, filename = %s
            WHERE id = %s
            """
            values = (name, company_name, department, phone, email, filename, post_id)
            self.cursor.execute(query, values)
            self.connection.commit()
            return True
        except Error as e:
            print(f"명함 수정 실패: {e}")
            return False
        finally:
            self.disconnect()

    # 명함 삭제
    def delete_post(self, post_id):
        self.connect()
        try:
            query = "DELETE FROM business_cards WHERE id = %s"
            self.cursor.execute(query, (post_id,))
            self.connection.commit()
            return True
        except Error as e:
            print(f"명함 삭제 실패: {e}")
            return False
        finally:
            self.disconnect()

    # 명함 전달
    def give_post(self, post_id, recipient_id):
        self.connect()
        try:
            query = """
            UPDATE business_cards
            SET user_id = %s
            WHERE id = %s
            """
            values = (recipient_id, post_id)
            self.cursor.execute(query, values)
            self.connection.commit()
            return True
        except Error as e:
            print(f"명함 전달 실패: {e}")
            return False
        finally:
            self.disconnect()
