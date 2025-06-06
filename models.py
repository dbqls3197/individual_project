import mysql.connector
from mysql.connector import Error
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
import qrcode
from io import BytesIO
import base64


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
                host='10.0.66.10',
                user='dbqls',
                password='1234',
                database='business_cards'
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
        except mysql.connector.Error as error:
            self.cursor = None


# DB에 연결 종료
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()


# 회원 가입
    def register_user(self, userid, username, name, password, email, phone, profile_picture):
        self.connect()
        try:
            checks = [
                ('userid', userid, "아이디가 이미 존재합니다."),
                ('username', username, "닉네임이 이미 존재합니다."),
                ('email', email, "이메일이 이미 존재합니다."),
                ('phone', phone, "핸드폰 번호가 이미 존재합니다.")
            ]
            
            for field, value, error_message in checks:
                if self.is_field_exists(field, value):
                    return False, error_message

            hashed_password = generate_password_hash(password)

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


# 사용자 정보 확인
    def get_user_by_id(self, user_id):
        self.connect()
        query = """
        SELECT id, userid, username, name, email, profile_picture, phone, created_at
        FROM users
        WHERE id = %s
        """
        self.cursor.execute(query, (user_id,))
        result = self.cursor.fetchone()
        return result
    

# 사용자 정보 수정
    def update_user(self, user_id, username, name, email, phone, profile_picture):
        try:
            self.connect()

            check_query = """
            SELECT username, email, phone FROM users 
            WHERE (username = %s OR email = %s OR phone = %s) AND userid != %s
            """
            self.cursor.execute(check_query, (username, email, phone, user_id))
            duplicates = self.cursor.fetchall()

            if duplicates:
                for duplicate in duplicates:
                    if duplicate['username'] == username:
                        return False, "이미 사용 중인 닉네임입니다."
                    if duplicate['email'] == email:
                        return False, "이미 사용 중인 이메일입니다."
                    if duplicate['phone'] == phone:
                        return False, "이미 사용 중인 전화번호입니다."

            if not profile_picture:
                profile_picture = None

            query = """
            UPDATE users 
            SET username = %s, name = %s, email = %s, phone = %s, profile_picture = %s
            WHERE userid = %s
            """
            values = (username, name, email, phone, profile_picture, user_id) 
            self.cursor.execute(query, values)
            self.connection.commit()

            if self.cursor.rowcount == 0:
                return False, "업데이트할 정보가 없습니다."
            return True, "사용자 정보가 성공적으로 업데이트되었습니다."
        except mysql.connector.Error as error:
            return False, f"DB 업데이트 실패: {error}"
        finally:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()


# 필드 중복 체크
    def is_field_exists(self, field, value):
        self.connect()
        try:
            query = f"SELECT 1 FROM users WHERE {field} = %s LIMIT 1"
            self.cursor.execute(query, (value,))
            return self.cursor.fetchone() is not None
        except mysql.connector.Error as e:
            return False
        

# 사용자 정보 조회
    def get_user_by_id(self, user_id):
        self.connect()
        try:
            query = "SELECT * FROM users WHERE userid = %s"
            self.cursor.execute(query, (user_id,))
            return self.cursor.fetchone()
        finally:
            self.disconnect()


# 회원 탈퇴
    def delete_user(self, user_id):
        self.connect()
        try:
            delete_posts_query = "DELETE FROM board_posts WHERE user_id = %s"
            self.cursor.execute(delete_posts_query, (user_id,))

            delete_received_posts_query = "DELETE FROM business_cards WHERE user_id = %s"
            self.cursor.execute(delete_received_posts_query, (user_id,))

            delete_user_query = "DELETE FROM users WHERE userid = %s"
            self.cursor.execute(delete_user_query, (user_id,))

            self.connection.commit()
            return True
        except Exception as e:
            self.connection.rollback()
            return False
        finally:
            self.disconnect()


# 로그인
    def login_user(self, userid, password):
        self.connect()
        try:
            query = "SELECT * FROM users WHERE userid = %s"
            self.cursor.execute(query, (userid,))
            user = self.cursor.fetchone()

            if user:
                if check_password_hash(user['password'], password):
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
    def insert_post(self, user_id, name, company_name, address, department, position, phone, email, filename):
        self.connect()
        try:
            query = """
            INSERT INTO my_business_cards (user_id, name, company_name, address, department, position, phone, email, filename)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (user_id, name, company_name, address, department, position, phone, email, filename)
            self.cursor.execute(query, values)
            self.connection.commit()
            return True
        except Error as e:
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
            return []
        finally:
            self.disconnect()


# 내 명함 수정
    def update_post(self, post_id, name, company_name, address, department, position, phone, email, filename):
        self.connect()
        try:
            self.cursor.execute("SELECT filename FROM my_business_cards WHERE id = %s", (post_id,))
            current_filename = self.cursor.fetchone()['filename']

            if not filename:
                filename = current_filename

            query = """
            UPDATE my_business_cards
            SET name = %s, company_name = %s, address = %s, department = %s, position = %s,
            phone = %s, email = %s, filename = %s
            WHERE id = %s
            """
            values = (name, company_name, department, address, position, phone, email, filename, post_id)
            self.cursor.execute(query, values)
            self.connection.commit()
            return True
        except Error as e:
            self.connection.rollback()
            return False
        finally:
            self.disconnect()


# 명함 조회
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
            return None
        finally:
            self.disconnect()

    def generate_qr(self, post):
        try:
            # vCard 형식으로 명함 정보 구성
            vcard = f"""BEGIN:VCARD
    VERSION:3.0
    FN:{post['name']}
    ORG:{post['company_name']}
    TITLE:{post['position']}
    ADR;TYPE=WORK:{post['address']}
    TEL;TYPE=WORK:{post['phone']}
    EMAIL:{post['email']}
    NOTE:부서: {post['department']}
    END:VCARD"""
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(vcard)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffered = BytesIO()
            img.save(buffered)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return img_str
        except Exception as e:
            print(f"QR 코드 생성 오류: {str(e)}")
            return None


# 명함 전체 조회
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
            return []
        finally:
            self.disconnect()


# 내 명함 삭제
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
            return []
        finally:
            self.disconnect()


# 받은 명함 삭제
    def delete_received_post(self, id, user_id):
        self.connect()
        try:
            query = "DELETE FROM business_cards WHERE id = %s AND user_id = %s"
            self.cursor.execute(query, (id, user_id))
            
            if self.cursor.rowcount == 0:
                return False
            
            self.connection.commit()
            return True
        
        except Error as e:
            return False
        finally:
            self.disconnect()


# 명함 전달
    def give_card(self, post_id, from_user_id, to_username):
        self.connect()
        try:
            query = "SELECT userid FROM users WHERE username = %s"  
            self.cursor.execute(query, (to_username,))
            recipient = self.cursor.fetchone()
            
            if not recipient:
                return False, f"'{to_username}' 닉네임을 가진 사용자를 찾을 수 없습니다."
            
            to_user_id = recipient['userid']  
            
            query = """
            SELECT * FROM my_business_cards 
            WHERE user_id = %s AND id = %s
            """
            self.cursor.execute(query, (from_user_id, post_id))
            card = self.cursor.fetchone()
            
            if not card:
                return False, "명함을 찾을 수 없습니다. 사용자 정보를 확인해 주세요."
            
            query = """
            INSERT INTO business_cards 
            (user_id, name, company_name, address, department, position, phone,
            email, filename, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            values = (to_user_id, card['name'], card['company_name'],
                    card['address'], card['department'], card['position'], 
                    card['phone'], card['email'], card['filename'])
            
            self.cursor.execute(query, values)
            self.connection.commit()
            
            return True, f"'{to_username}' 님에게 명함을 전달했습니다."
            
        except Error as e:
            self.connection.rollback()
            return False, f"명함 전달에 실패했습니다: {str(e)}"
        finally:
            self.disconnect()


# 명함데이터를 데이터베이스에서 조회
    def get_user_cards(self, user_id):
        self.connect()
        try:
            query = "SELECT * FROM my_business_cards WHERE user_id = %s"
            self.cursor.execute(query, (user_id,))
            return self.cursor.fetchall()
        finally:
            self.disconnect()

# 게시판에 게시글 저장
    def insert_board_post(self, user_id, title, content, filename=None):
        self.connect()
        try:
            query = """
            INSERT INTO board_posts 
            (user_id, title, content, filename, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, NOW(), NOW())
            """
            values = (user_id, title, content, filename)
            self.cursor.execute(query, values)
            self.connection.commit()
            return True
        except Error as e:
            return False
        finally:
            self.disconnect()

# 게시글 목록 페이징
    def get_board_posts(self, page=1, per_page=10):
        self.connect()
        try:
            offset = (page - 1) * per_page

            query = """
            SELECT bp.*, u.username 
            FROM board_posts bp 
            JOIN users u ON bp.user_id = u.userid 
            ORDER BY bp.created_at DESC 
            LIMIT %s OFFSET %s
            """
            self.cursor.execute(query, (per_page, offset))
            posts = self.cursor.fetchall()

            count_query = "SELECT COUNT(*) as total FROM board_posts"
            self.cursor.execute(count_query)
            total_posts_result = self.cursor.fetchone()

            total_posts = total_posts_result["total"] if total_posts_result else 0

            return posts, total_posts
        finally:
            self.disconnect()


# 게시글 및 댓글 조회
    def get_post_with_comments(self, id):
        try:
            self.connect()
            
            sql_post = "SELECT * FROM board_posts WHERE id = %s"
            self.cursor.execute(sql_post, (id,))
            post = self.cursor.fetchone()

            if not post:
                return None, []

            sql_comments = """
                SELECT comments.id, comments.user_id, users.username, comments.content, comments.created_at
                FROM comments
                JOIN users ON comments.user_id = users.userid
                WHERE comments.post_id = %s
                ORDER BY comments.created_at ASC
                """
            self.cursor.execute(sql_comments, (id,))
            comments = self.cursor.fetchall()


            return post, comments

        except mysql.connector.Error as error:
            return None, []
        finally:
            self.disconnect()


# 댓글 추가
    def add_comment(self, post_id, user_id, content):
        try:
            self.connect()
            sql = "INSERT INTO comments (post_id, user_id, content, created_at, updated_at) VALUES (%s, %s, %s, NOW(), NOW())"
            values = (post_id, user_id, content)
            self.cursor.execute(sql, values)
            self.connection.commit()
        except mysql.connector.Error as error:
            raise error
        finally:
            self.disconnect()


# 댓글 삭제
    def delete_comment(self, comment_id, user_id):
        try:
            self.connect()  
            query = "DELETE FROM comments WHERE id = %s AND user_id = %s"
            self.cursor.execute(query, (comment_id, user_id))
            self.connection.commit()  

            if self.cursor.rowcount > 0:
                print("댓글 삭제 성공!")
            else:
                print("삭제할 댓글이 없음.")
        except Exception as e:
            print("댓글 삭제 오류:", str(e))
        finally:
            self.disconnect()  


# 조회수증가
    def update_views(self, id):
        try:
            self.connect()
            sql = "UPDATE board_posts  SET views = views + 1 WHERE id = %s"
            value = (id,)
            self.cursor.execute(sql, value)
            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            self.connection.rollback()
            return False
        finally:
            self.disconnect()


# 게시글 조회
    def get_board_post(self, post_id):
        try:
            self.connect()
            sql = "SELECT * FROM board_posts WHERE id = %s"
            value = (post_id,)
            self.cursor.execute(sql, value)
            post = self.cursor.fetchone()
            if not post:
                raise ValueError("게시글을 찾을 수 없습니다.")
            return post
        except mysql.connector.Error as error:
            return None
        finally:
            self.disconnect()


# 게시글 수정
    def update_board_post(self, id, title, content, filename=None):
        try:
            self.connect()
            if filename:
                # 새 파일이 업로드된 경우
                query = """
                UPDATE board_posts
                SET title = %s, content = %s, filename = %s, updated_at = NOW()
                WHERE id = %s
                """
                values = (title, content, filename, id)
            else:
                # 파일이 변경되지 않은 경우, 기존 파일 유지
                query = """
                UPDATE board_posts
                SET title = %s, content = %s, updated_at = NOW()
                WHERE id = %s
                """
                values = (title, content, id)

            self.cursor.execute(query, values)
            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            return False
        finally:
            self.disconnect()


# 게시글 삭제
    def delete_board(self, id):
        try:
            self.connect()
            sql = "DELETE FROM board_posts WHERE id = %s"
            value = (id,)

            self.cursor.execute(sql, value)
            self.connection.commit()

            return True
        except mysql.connector.Error as error:
            return False
        finally:
            self.disconnect()

