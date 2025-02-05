from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory, session, flash
import os
import mysql.connector
from datetime import datetime
from models import DBManager
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# 업로드 폴더 설정
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 비밀 번호와 세션 키
app.secret_key = '1234'

# DB 연결 및 매니저 설정
manager = DBManager() 


# 메인 페이지
@app.route('/')
def index():
    if 'userid' not in session:
        return redirect('/login')
    user_id = session.get('userid')
    posts = manager.get_user_posts(user_id) 
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


# 회원 탈퇴
@app.route('/delete_account', methods=["GET", "POST"])
def delete_account():
    if 'userid' not in session:
        return redirect('/login')
    
    user_id = session.get('userid')
    
    if request.method == "POST":
        password = request.form['password']
        user = manager.get_user_by_id(user_id)
        
        if user is None:
            flash('사용자 정보를 찾을 수 없습니다.', 'danger')
            return redirect(url_for('delete_account'))
        
        if not check_password_hash(user['password'], password):
            flash('비밀번호가 일치하지 않습니다.', 'danger')
            return redirect(url_for('delete_account'))
        
        if manager.delete_user(user_id):
            flash('회원 탈퇴가 완료되었습니다.', 'success')
            session.clear()
            return redirect(url_for('login'))
        else:
            flash('회원 탈퇴에 실패했습니다. 다시 시도해 주세요.', 'danger')
            return redirect(url_for('delete_account'))
            
    return render_template('delete_account.html')


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
        address = request.form['address']
        department = request.form['department']
        position = request.form['position']
        phone = request.form['phone']
        email = request.form['email']
        file = request.files['file']
        filename = file.filename if file else None

        if filename:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if manager.insert_post(user_id, name, company_name, address, department, position, phone, email, filename):
            flash('명함이 성공적으로 추가되었습니다!', 'success')  
            return redirect('/') 
        else:
            flash('명함 추가 실패', 'danger') 
            return redirect(url_for('add_post'))

    return render_template('add.html')


# 내 명함 보기
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
        address = request.form['address']
        department = request.form['department']
        position = request.form['position']
        phone = request.form['phone']
        email = request.form['email']
        file = request.files['file']
        filename = file.filename if file else None
        
        if filename:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        if manager.update_post(id, name, company_name, address, department, position, phone, email, filename):
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
        
        success, message = manager.give_card(card_id, session['userid'], to_username)
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
        return redirect(url_for('give_card'))

    return render_template('give_card.html', cards=user_cards)


# 게시판 목록
@app.route('/board')
def board_list():
    if 'userid' not in session:
        return redirect('/login')

    page = request.args.get('page', 1, type=int)
    per_page = 10  

    posts, total_posts = manager.get_board_posts(page, per_page)

    total_pages = max((total_posts + per_page - 1) // per_page, 1)

    return render_template('board.html', posts=posts, page=page, total_pages=total_pages)


# 게시글 작성
@app.route('/board/write', methods=['GET', 'POST'])
def board_write():
    if 'userid' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        user_id = session['userid']
        title = request.form['title']
        content = request.form['content']
        file = request.files.get('file')
        filename = file.filename if file else None
        
        if filename:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        if manager.insert_board_post(user_id, title, content, filename):
            flash('게시글이 성공적으로 작성되었습니다.', 'success')
            return redirect(url_for('board_list'))
        else:
            flash('게시글 작성에 실패했습니다.', 'danger')
    
    return render_template('board_write.html')


# 게시글 내용보기
@app.route('/board/view/<int:id>')
def board_view_post(id):
    manager.update_views(id)  # 조회수 증가
    post, comments = manager.get_post_with_comments(id)
    
    if not post:
        return "게시글을 찾을 수 없습니다.", 404

    return render_template('board_view.html', post=post, comments=comments)

# 댓글 추가
@app.route('/add_comment', methods=['POST'])
def add_comment():
    try:
        if 'userid' not in session:
            flash('로그인이 필요합니다.')
            return redirect(url_for('login'))
        
        post_id = request.form.get('post_id')
        content = request.form.get('content')

        if not post_id or not content:
            flash('댓글 내용을 입력하세요.')
            return redirect(request.referrer)  

        # 댓글 저장
        manager.add_comment(post_id, session['userid'], content)
        flash('댓글이 등록되었습니다.')

    except Exception as e:
        flash('댓글 등록 중 오류 발생.')
    
    return redirect(url_for('board_view_post', id=post_id))


# 댓글 삭제
@app.route('/delete_comment', methods=['POST'])
def delete_comment():
    if 'userid' not in session:
        flash('로그인이 필요합니다.')
        return redirect(url_for('login'))
    
    comment_id = request.form.get('comment_id')

    try:
        manager.delete_comment(comment_id, session['userid'])
        flash('댓글이 삭제되었습니다.')
    except Exception as e:
        flash('댓글 삭제 중 오류 발생: ' + str(e))
    
    post_id = request.form.get('post_id') 
    return redirect(url_for('board_view_post', id=post_id))

    

# 게시글 수정
@app.route('/board/edit/<int:id>', methods=['GET', 'POST'])
def edit_board_post(id):
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        file = request.files.get('file')
        
        filename = None
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        success = manager.update_board_post(id, title, content, filename)
        if success:
            flash('게시글이 수정되었습니다.')
            return redirect(url_for('view_board_post', id=id))
        else:
            flash('게시글 수정에 실패했습니다.')
            return redirect(url_for('edit_board_post', id=id))
    else:
        post = manager.get_board_post(id)
        if post:
            return render_template('board_edit.html', post=post)
        else:
            flash('게시글을 찾을 수 없습니다.')
            return redirect(url_for('board'))


# 게시글 내용보기(수정)
@app.route('/board/view/<int:id>')
def view_board_post(id):
    post = manager.get_board_post(id)
    
    if post:
        return render_template('board_view.html', post=post)
    else:
        flash('게시글을 찾을 수 없습니다.')
        return redirect(url_for('board'))


# 게시글 삭제
@app.route('/board/delete/<int:id>')
def delete_board_post(id):
    if 'userid' not in session:
        flash("로그인이 필요합니다.", "danger")
        return redirect(url_for('login'))
    
    user_id = session['userid']  
    post = manager.get_board_post(id)  

    if post and post['user_id'] == user_id:
        if manager.delete_board(id): 
            flash('게시글이 삭제되었습니다.', 'success')
        else:
            flash('게시글 삭제에 실패했습니다.', 'danger')
    else:
        flash('삭제 권한이 없습니다.', 'danger')

    return redirect(url_for('board_list'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
