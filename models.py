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
    def register_user(self, userid, username, name, password, email, phone, profile_picture):
        self.connect()
        try:
            # 중복 체크를 순차적으로 수행
            checks = [
                ('userid', userid, "아이디가 이미 존재합니다."),
                ('username', username, "닉네임이 이미 존재합니다."),
                ('email', email, "이메일이 이미 존재합니다."),
                ('phone', phone, "핸드폰 번호가 이미 존재합니다.")
            ]
            
            for field, value, error_message in checks:
                if self.is_field_exists(field, value):
                    return False, error_message

            hashed_password = self.hash_password(password)

            query = """
            INSERT INTO users (userid, username, name, password, email, phone, profile_picture)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (userid, username, name, hashed_password, email, phone, profile_picture)
            self.cursor.execute(query, values)
            self.connection.commit()
            return True, "회원가입이 완료되었습니다."
        except Error as e:
            return False, f"회원가입 실패: {e}"
        finally:
            self.disconnect()

    def is_field_exists(self, field, value):
        self.connect()  # 연결 상태 확인 및 연결
        try:
            query = f"SELECT 1 FROM users WHERE {field} = %s LIMIT 1"
            self.cursor.execute(query, (value,))
            return self.cursor.fetchone() is not None
        except mysql.connector.Error as e:
            print(f"{field} 중복 체크 중 오류 발생: {e}")
            return False



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


    # 내 명함 가져오기
    def get_all_posts_user(self, user_id):
        self.connect()
        try:
            query = """
            SELECT * FROM my_business_cards 
            WHERE user_id = %s
            ORDER BY id DESC
            """
            self.cursor.execute(query, (user_id,))
            return self.cursor.fetchall()
        except Error as e:
            print(f"명함 목록 조회 실패: {e}")
            return []
        finally:
            self.disconnect()


    # 내 명함 수정
    def update_post(self, post_id, name, company_name, department, position, phone, email, filename):
        self.connect()
        try:
            query = """
            UPDATE my_business_cards
            SET name = %s, company_name = %s, department = %s, position = %s,phone = %s, email = %s, filename = %s
            WHERE id = %s
            """
            values = (name, company_name, department, position, phone, email, filename, post_id)
            self.cursor.execute(query, values)
            self.connection.commit()
            return True
        except Error as e:
            print(f"명함 수정 실패: {e}")
            return False
        finally:
            self.disconnect()

    def get_post_by_id(self, post_id, user_id):
        self.connect()
        try:
            query = """
            SELECT * FROM my_business_cards 
            WHERE id = %s AND user_id = %s
            """
            self.cursor.execute(query, (post_id, user_id))
            return self.cursor.fetchone()
        except Error as e:
            print(f"명함 조회 실패: {e}")
            return None
        finally:
            self.disconnect()

    def get_user_posts(self, user_id):
        self.connect()
        try:
            query = """
            SELECT * FROM my_business_cards 
            WHERE user_id = %s
            """
            self.cursor.execute(query, (user_id,))
            return self.cursor.fetchall()
        except Error as e:
            print(f"명함 목록 조회 실패: {e}")
            return []
        finally:
            self.disconnect()


    # 내명함 삭제
    def delete_post(self, post_id, user_id):
        self.connect()
        try:
            query = """
            DELETE FROM my_business_cards 
            WHERE id = %s AND user_id = %s
            """
            self.cursor.execute(query, (post_id, user_id))
            self.connection.commit()
            return True
        except Error as e:
            print(f"명함 삭제 실패: {e}")
            return False
        finally:
            self.disconnect()

# 받은 명함 전체보기
    def get_received_posts(self, user_id):
        self.connect()
        try:
            query = """
            SELECT * 
            FROM business_cards 
            WHERE user_id = %s
            """
            self.cursor.execute(query, (user_id,))
            posts = self.cursor.fetchall()
            return posts
        except Exception as e:
            print(f"받은 명함 조회 실패: {e}")
            return []
        finally:
            self.disconnect()

    def delete_received_post(self, id, user_id):
        self.connect()
        try:
            # 받은 명함 테이블에서 삭제
            query = "DELETE FROM business_cards WHERE id = %s AND user_id = %s"
            self.cursor.execute(query, (id, user_id))
            
            if self.cursor.rowcount == 0:
                return False
            
            self.connection.commit()
            return True
        
        except Error as e:
            print(f"받은 명함 삭제 실패: {e}")
            return False
        finally:
            self.disconnect()



    def give_card(self, post_id, from_user_id, to_username):
        self.connect()
        try:
            # 받는 사람의 userid 조회 (컬럼명 주의!)
            query = "SELECT userid FROM users WHERE username = %s"  # userid로 변경
            self.cursor.execute(query, (to_username,))
            recipient = self.cursor.fetchone()
            
            if not recipient:
                return False, f"'{to_username}' 닉네임을 가진 사용자를 찾을 수 없습니다."
            
            to_user_id = recipient['userid']  # userid로 변경
            
            # 명함 정보 조회
            query = """
            SELECT * FROM my_business_cards 
            WHERE user_id = %s AND id = %s
            """
            self.cursor.execute(query, (from_user_id, post_id))
            card = self.cursor.fetchone()
            
            if not card:
                return False, "명함을 찾을 수 없습니다. 사용자 정보를 확인해 주세요."
            
            # 명함을 받은 사람의 보관함에 저장
            query = """
            INSERT INTO business_cards 
            (user_id, name, company_name, department, position, phone,
            email, filename, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            values = (to_user_id, card['name'], card['company_name'],
                    card['department'], card['position'], card['phone'],
                    card['email'], card['filename'])
            
            print(f"Debug - Inserting with values: {values}")  # 디버깅용
            
            self.cursor.execute(query, values)
            self.connection.commit()
            
            return True, f"'{to_username}' 님에게 명함을 전달했습니다."
            
        except Error as e:
            print(f"명함 전달 실패: {e}")
            self.connection.rollback()
            return False, f"명함 전달에 실패했습니다: {str(e)}"
        finally:
            self.disconnect()

    def get_user_cards(self, user_id):
        self.connect()
        try:
            query = "SELECT * FROM my_business_cards WHERE user_id = %s"
            self.cursor.execute(query, (user_id,))
            return self.cursor.fetchall()
        finally:
            self.disconnect()


