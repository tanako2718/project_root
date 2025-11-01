document.addEventListener('DOMContentLoaded', () => {
    // ページ上のすべての削除ボタンを取得
    const deleteButtons = document.querySelectorAll('.delete-btn');
    
    // 削除ボタンごとにイベントリスナーを設定
    deleteButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            const todoId = event.target.getAttribute('data-id');
            
            if (todoId && confirm('本当にこのToDoを削除してもよろしいですか？')) {
                // 削除用フォームの要素を取得
                const form = document.createElement('form');
                form.method = 'POST';
                // Flaskの削除URLを動的に設定
                form.action = `/todo/delete/${todoId}`; 
                
                // フォームを一時的にbodyに追加して送信
                document.body.appendChild(form);
                form.submit();
            }
        });
    });
});