import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, current_user, login_required

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
# ========== データベース設定 ==========
# PostgreSQL接続設定
# 形式: postgresql://ユーザー名:パスワード@ホスト:ポート/データベース名
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Tanako1146@localhost:5432/todo_calendar_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)

# Flask-Loginの設定
login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)

# ========== モデル定義 ==========
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    mail_address = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    schedules = db.relationship('Schedule', backref='users', lazy=True, cascade='all, delete-orphan')

    def get_id(self):
        return str(self.user_id)

class Schedule(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    users_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    item = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    detail = db.Column(db.Text)
    starting_day = db.Column(db.Date, nullable=False)
    ending_day = db.Column(db.Date)
    starting_time = db.Column(db.Time)
    ending_time = db.Column(db.Time)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ========== Flask-Login設定 ==========
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ========== データベース初期化 ==========
with app.app_context():
    db.create_all()
    print("データベーステーブルを作成しました")

# ========== ルーティング ==========
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # フォームからのデータ取得
        mail_address = request.form.get('mailAddress')
        password = request.form.get('password')
        # メアドをもとにユーザーを検索
        user = User.query.filter_by(mail_address=mail_address).first()
        # バリデーション（必須項目のチェック）
#        if user:
#           target_user_id = user.user_id
#            print(f"Found user ID: {target_user_id}")
#            flash('ログイン成功', 'success')
#            return redirect(url_for('index', user_id=target_user_id))  # ログイン成功後、indexにリダイレクト
        if user and check_password_hash(user.password, password):
            login_user(user)  # ユーザーをログインさせる
            return redirect('index')
        if not mail_address or not password:
            flash('すべての項目を入力してください', 'error')
            return redirect(url_for('login'))
        else:
            flash('メールアドレスが間違ってます', 'error')
        
        return redirect(url_for('login'))  # ログイン失敗、やり直し
    # GETリクエスト（単にページを表示するとき）の処理
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # POSTリクエスト（フォームが送信されたとき）の処理
    if request.method == 'POST':
        # フォームからのデータ取得
        user_name = request.form.get('userName')
        mail_address = request.form.get('mailAddress')
        password = request.form.get('password')
        
        # 1. バリデーション（必須項目のチェック）
        if not user_name or not mail_address or not password:
            flash('すべての項目を入力してください', 'error')
            return redirect(url_for('register'))
            
        # 2. メールアドレスの重複チェック
        if User.query.filter_by(mail_address=mail_address).first():
            flash('そのメールアドレスはすでに使用されています', 'error')
            return redirect(url_for('register'))
        
        password_hash = generate_password_hash(password)  # ハッシュ化

        # 3. ユーザーオブジェクトを作成し、DBに保存
        try:
            new_user = User(
                user_name=user_name,
                mail_address=mail_address,
                password=password_hash # コードの保守性と見やすさのための変数使用
            )
            db.session.add(new_user)
            db.session.commit()
            
            flash('登録が完了しました。ログインしてください', 'success')
            # 登録成功後、ログインページにリダイレクトすることを想定
            return redirect(url_for('login')) # 便宜上indexにリダイレクト
            
        except Exception as e:
            db.session.rollback()
            flash('登録中にエラーが発生しました', 'error')
            print(f"Error: {e}")
            return redirect(url_for('register'))
            
    # GETリクエスト（単にページを表示するとき）の処理
    return render_template('register.html')

@app.route('/index')
@login_required
def index():
    # データベースからTodoを取得
    todos = Schedule.query.filter_by(users_id=current_user.user_id).order_by(Schedule.starting_day).all()

    # スケジュールをJavaScriptに渡すために整形（日付をISO形式に）
    schedule_data = []
    for todo in todos:
        schedule_data.append({
            'id': todo.id,
            'item': todo.item,
            'content': todo.content,
            'starting_day': todo.starting_day.isoformat() # Dateオブジェクトを 'YYYY-MM-DD' 形式の文字列に変換
        })
    
    return render_template('index.html', todos=todos, schedule_data=schedule_data) # schedule_dataもindex.htmlに渡す

# Todo追加
@app.route('/todo/add', methods=['POST'])
@login_required
def add_todo():

    item = request.form.get('item')
    content = request.form.get('content')
    detail = request.form.get('detail')
    starting_day = request.form.get('starting_day')
    
    # バリデーション
    if not item or not content or not starting_day:
        flash('項目、予定、締め切りは必須です', 'error')
        return redirect(url_for('index'))
    
    try:
        new_todo = Schedule(
            users_id=current_user.user_id,
            item=item,
            content=content,
            detail=detail,
            starting_day=datetime.strptime(starting_day, '%Y-%m-%d').date()
        )
        db.session.add(new_todo)
        db.session.commit() #操作完了
        flash('Todoを追加しました', 'success')
    except Exception as e:
        db.session.rollback()
        flash('エラーが発生しました', 'error')
        print(f"Error: {e}")
    
    return redirect(url_for('index'))

@app.route('/todo/delete/<int:todo_id>')
@login_required
def delete_todo(todo_id):

    todo = Schedule.query.get_or_404(todo_id)
    
    # 自分のTodoか確認
    if todo.users_id != current_user.user_id:
        flash('権限がありません', 'error')
        return redirect(url_for('index'))
    
    try:
        db.session.delete(todo)
        db.session.commit()
        flash('Todoを削除しました', 'success')
    except Exception as e:
        db.session.rollback()
        flash('エラーが発生しました', 'error')
        print(f"Error: {e}")
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
