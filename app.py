from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import os
import mysql.connector
from datetime import datetime
from models import DBManager

app = Flask(__name__)

# 업로드 폴더 설정
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# DB 연결 및 매니저 설정
manager = DBManager()

# 목록보기
@app.route('/')
def index():
    posts = manager.get_all_posts()  # DB에서 모든 명함 정보를 가져옵니다.
    return render_template('index.html', posts=posts)

# 내용보기
@app.route('/post/<int:id>')
def view_post(id):
    post = manager.get_post_by_id(id)  # 특정 명함 정보를 가져옵니다.
    return render_template('view.html', post=post)

# 명함 추가
@app.route('/post/add', methods=["GET", "POST"])
def add_post():
    if request.method == "POST":
        title = request.form['title']
        content = request.form['content']

        # 첨부파일 한 개
        file = request.files['file']
        filename = file.filename if file else None

        if filename:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if manager.insert_post(title, content, filename):
            return redirect('/')
        return '게시글 추가 실패', 400
    return render_template('add.html')

# 명함 수정
@app.route('/post/edit/<int:id>', methods=["GET", "POST"])
def edit_post(id):
    post = manager.get_post_by_id(id)
    if request.method == "POST":
        title = request.form['title']
        content = request.form['content']

        file = request.files['file']
        filename = file.filename if file else None

        if filename:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if manager.update_post(id, title, content, filename):
            return redirect('/')
        return '게시글 수정 실패', 400
    return render_template('edit.html', post=post)

# 명함 삭제
@app.route('/post/delete/<int:id>')
def delete_post(id):
    if manager.delete_post(id):
        return redirect(url_for('index'))
    return '게시글 삭제 실패', 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
