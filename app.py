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

# 목록보기 
@app.route('/')
def index():
    posts = manager.get_all_posts()  
    return render_template('index.html', posts=posts)


# 회원가입
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        userid = request.form['userid']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
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

        success, message = manager.register_user(userid, password, email, username, phone, filename)
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
            flash("로그인 성공!", "success")
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
            return redirect('/')
        return '명함 추가 실패', 400
    return render_template('add.html')


# 내 명함 내용보기
@app.route('/view')
def view_posts():
    user_id = session.get('userid')  # 세션에서 로그인한 유저 ID 가져오기
    posts = manager.get_all_posts_user(user_id)  # 유저의 명함만 가져오기
    if not posts:
        print("명함이 없습니다.")  # 디버깅용 로그
    
    return render_template('view.html', posts=posts)



# 명함 수정
@app.route('/post/edit/<int:id>', methods=["GET", "POST"])
def edit_post(id):
    post = manager.get_post_by_id(id)
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

# 명함 삭제
@app.route('/post/delete/<int:id>')
def delete_post(id):
    if manager.delete_post(id):
        return redirect(url_for('index'))
    return '명함 삭제 실패', 400

# 명함 전달 기능 (받은 명함 목록)
@app.route('/post/give/<int:id>', methods=["GET", "POST"])
def give_post(id):
    if request.method == "POST":
        recipient_id = request.form['recipient_id']  # 받은 사람의 ID
        if manager.give_post(id, recipient_id):
            return redirect('/')
        return '명함 전달 실패', 400
    post = manager.get_post_by_id(id)
    return render_template('give.html', post=post)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
