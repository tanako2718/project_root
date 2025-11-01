from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
#dammy data
todos = [
    {
        'id': 1,
        'item': '学業',
        'content': '数学の課題提出',
        'detail': '微分積分の問題集 p.45-52',
        'starting_day': date(2025, 10, 20)
    },
    {
        'id': 2,
        'item': 'バイト',
        'content': 'カフェバイト',
        'detail': '夕方シフト 17:00-21:00',
        'starting_day': date(2025, 10, 18)
    },
    {
        'id': 3,
        'item': 'サークル',
        'content': 'サークルミーティング',
        'detail': '新歓イベントの企画会議',
        'starting_day': date(2025, 10, 22)
    }
]

next_id = 4

@app.route('/')
def index():
    # 締め切り順にソート
    sorted_todos = sorted(todos, key=lambda x: x['starting_day'])
    return render_template('index.html', todos=sorted_todos)

# Todo追加
@app.route('/todo/add', methods=['POST'])
def add_todo():
    global next_id
    # 変数にフォームデータを格納
    item = request.form.get('item')
    content = request.form.get('content')
    detail = request.form.get('detail')
    starting_day = request.form.get('starting_day')
    
    # バリデーション
    if not item or not content or not starting_day:
        flash('項目、予定、締め切りは必須です', 'error')
        return redirect(url_for('index'))
    
    try:
        new_todo = {
            'id': next_id,
            'item': item,
            'content': content,
            'detail': detail,
            'starting_day': datetime.strptime(starting_day, '%Y-%m-%d').date()
        }
        todos.append(new_todo)
        next_id += 1
        flash('Todoを追加しました', 'success')
    except Exception as e:
        flash('エラーが発生しました', 'error')
        print(f"Error: {e}")
    
    return redirect(url_for('index'))

@app.route('/todo/delete/<int:todo_id>', methods=['POST'])
def delete_todo(todo_id):
    global todos
    todos = [todo for todo in todos if todo['id'] != todo_id]
    flash('Todoを削除しました', 'success')

    # 削除が成功したかを確認
    if len(todos) < len(todos) + 1:
        flash(f"ToDo (ID: {todo_id}) を削除しました", 'success')
    else:
        flash(f"ToDo (ID: {todo_id}) が見つかりませんでした", 'error')
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)