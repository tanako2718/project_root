from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
# ========== データベース設定 ==========
# PostgreSQL接続設定
# 形式: postgresql://ユーザー名:パスワード@ホスト:ポート/データベース名
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Tanako1146@localhost:5432/todo_calendar_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ========== モデル定義 ==========
class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    mail_address = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    schedules = db.relationship('Schedule', backref='user', lazy=True, cascade='all, delete-orphan')

class Schedule(db.Model):
    __tablename__ = 'schedule'
    id = db.Column(db.Integer, primary_key=True)
    users_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    item = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    detail = db.Column(db.Text)
    starting_day = db.Column(db.Date, nullable=False)
    ending_day = db.Column(db.Date)
    starting_time = db.Column(db.Time)
    ending_time = db.Column(db.Time)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ========== データベース初期化 ==========
with app.app_context():
    db.create_all()
    print("データベーステーブルを作成しました")
    
    # 開発用テストユーザーの作成（初回のみ）
    if User.query.count() == 0:
        test_user = User(
            user_name='テストユーザー',
            mail_address='test@example.com',
            password='test123'  # 本番環境ではハッシュ化必須
        )
        db.session.add(test_user)
        db.session.commit()
        print("テストユーザーを作成しました")

#dammy data
# todos = [
#     {
#         'id': 1,
#         'item': '学業',
#         'content': '数学の課題提出',
#         'detail': '微分積分の問題集 p.45-52',
#         'starting_day': date(2025, 10, 20)
#     },
#     {
#         'id': 2,
#         'item': 'バイト',
#         'content': 'カフェバイト',
#         'detail': '夕方シフト 17:00-21:00',
#         'starting_day': date(2025, 10, 18)
#     },
#     {
#         'id': 3,
#         'item': 'サークル',
#         'content': 'サークルミーティング',
#         'detail': '新歓イベントの企画会議',
#         'starting_day': date(2025, 10, 22)
#     }
# ]

# next_id = 4

@app.route('/')
def login():
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

        # 3. ユーザーオブジェクトを作成し、DBに保存
        try:
            # 【重要】本番環境では必ずpasswordをハッシュ化してください（例：werkzeug.securityのgenerate_password_hashを使用）
            new_user = User(
                user_name=user_name,
                mail_address=mail_address,
                password=password # 現時点では平文で保存
            )
            db.session.add(new_user)
            db.session.commit()
            
            flash('登録が完了しました。ログインしてください', 'success')
            # 登録成功後、ログインページにリダイレクトすることを想定
            return redirect(url_for('index')) # 便宜上indexにリダイレクト
            
        except Exception as e:
            db.session.rollback()
            flash('登録中にエラーが発生しました', 'error')
            print(f"Error: {e}")
            return redirect(url_for('register'))
            
    # GETリクエスト（単にページを表示するとき）の処理
    return render_template('register.html')

@app.route('/index')
def index():
# 開発用：user_id=1を固定で使用
    user_id = 1
    
    # データベースからTodoを取得
    todos = Schedule.query.filter_by(users_id=user_id).order_by(Schedule.starting_day).all()

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
def add_todo():
    user_id = 1  # 開発用の仮ユーザーID
    
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
            users_id=user_id,
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
def delete_todo(todo_id):
    user_id = 1  # 開発用の仮ユーザーID
    
    todo = Schedule.query.get_or_404(todo_id)
    
    # 自分のTodoか確認
    if todo.users_id != user_id:
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