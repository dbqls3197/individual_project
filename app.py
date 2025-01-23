from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory, session, flash
import os
import mysql.connector
from datetime import datetime
from models import DBManager

app = Flask(__name__)

# 업로드 폴더 설정
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 비밀 번호와 세션 키
app.secret_key = '1234'

# DB 연결 및 매니저 설정
manager = DBManager()


@app.route('/')
def index():
    if 'userid' not in session:
        return redirect('/login')
    user_id = session.get('userid')
    posts = manager.get_user_posts(user_id)  # 사용자의 모든 명함 가져오기
    return render_template('index.html', posts=posts)


# 회원가입
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        userid = request.form['userid']
        username = request.form['username']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("비밀번호가 일치하지 않습니다", "danger")
            return redirect(url_for('register'))

        profile_picture = request.files.get('profile_picture')
        if profile_picture:
            filename = profile_picture.filename
            profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = None  

        success, message = manager.register_user(userid, username, name, password, email, phone, filename)
        if success:
            flash(message, "success")
            return redirect(url_for('login'))
        else:
            flash(message, "danger")
            return redirect(url_for('register'))

    return render_template('register.html')


# 로그인
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        userid = request.form['userid']
        password = request.form['password']
        
        success, message = manager.login_user(userid, password)
        
        if success:
            session['userid'] = userid  
            return redirect(url_for('index'))
        else:
            flash(message, "danger")  
            return redirect(url_for('login'))

    return render_template('login.html')


# 로그아웃
@app.route('/logout')
def logout():
    session.pop('userid', None)
    flash("로그아웃되었습니다.", "info")
    return redirect(url_for('login'))


# 명함 추가
@app.route('/post/add', methods=["GET", "POST"])
def add_post():
    if request.method == "POST":
        user_id = session['userid']
        name = request.form['name']
        company_name = request.form['company_name']
        department = request.form['department']
        position = request.form['position']
        phone = request.form['phone']
        email = request.form['email']
        file = request.files['file']
        filename = file.filename if file else None

        if filename:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if manager.insert_post(user_id, name, company_name, department, position, phone, email, filename):
            flash('명함이 성공적으로 추가되었습니다!', 'success')  
            return redirect('/') 
        else:
            flash('명함 추가 실패', 'danger') 
            return redirect(url_for('add_post'))

    return render_template('add.html')


# 내 명함 내용보기
@app.route('/view')
def view_posts():
    user_id = session.get('userid')  
    posts = manager.get_all_posts_user(user_id) 
    if not posts:
        print("명함이 없습니다.")  
    
    return render_template('view.html', posts=posts)


# 명함 수정
@app.route('/edit/<int:id>', methods=["GET", "POST"])
def edit_post(id):
    if 'userid' not in session:
        return redirect('/login')
    
    user_id = session.get('userid')
    post = manager.get_post_by_id(id, user_id)
    
    if post is None:
        return "명함을 찾을 수 없습니다.", 404
    
    if request.method == "POST":
        name = request.form['name']
        company_name = request.form['company_name']
        department = request.form['department']
        position = request.form['position']
        phone = request.form['phone']
        email = request.form['email']
        file = request.files['file']
        filename = file.filename if file else None
        
        if filename:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        if manager.update_post(id, name, company_name, department, position, phone, email, filename):
            return redirect('/')
        return '명함 수정 실패', 400
        
    return render_template('edit.html', post=post)
    
# 내 명함 삭제
@app.route('/delete/<int:id>', methods=['GET'])
def delete_post(id):
    if 'userid' not in session:
        return redirect('/login')
    
    user_id = session.get('userid')
    if manager.delete_post(id, user_id):
        flash('명함이 삭제되었습니다.','success')
        return redirect('/view')
    return '명함 삭제 실패', 400

# 받은 명함 조회
@app.route('/received')
def received_posts():
    if 'userid' not in session:
        return redirect(url_for('login'))

    user_id = session['userid']
    posts = manager.get_received_posts(user_id)  
    return render_template('storage_box.html', posts=posts)

    
# 받은 명함 삭제
@app.route('/delete_received/<int:id>', methods=['GET'])
def delete_received_post(id):
    if 'userid' not in session:
        return redirect('/login')
    
    user_id = session.get('userid')
    if manager.delete_received_post(id, user_id):
        
        return redirect('/received')
    return '받은 명함 삭제 실패', 400

# 명함 보내기
@app.route('/give_card', methods=['GET', 'POST'])
def give_card():
    if 'userid' not in session:
        return redirect('/login')
    
    # 사용자의 명함 목록을 가져옴
    user_cards = manager.get_user_cards(session['userid'])
    
    if request.method == 'POST':
        card_id = request.form['card_id']
        to_username = request.form['to_username']
        
        print(f"Attempting to give card {card_id} to {to_username}")  # 디버깅 출력
        success, message = manager.give_card(card_id, session['userid'], to_username)
        
        print(f"Result: success={success}, message={message}")  # 디버깅 출력
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
        return redirect(url_for('give_card'))

    # GET 요청일 때 명함 목록과 함께 템플릿 렌더링
    return render_template('give_card.html', cards=user_cards)







if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
