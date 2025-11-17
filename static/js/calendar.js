// Python (Flask) から渡されたスケジュールデータ
// Jinja2の safe フィルターと tojson フィルターを使用して安全にJSONを埋め込み
// 実際のアプリケーションでは、この行はindex.htmlのテンプレート内で動作します。
// ここでは仮の値として空の配列を定義します。
const scheduleData = typeof
__schedule_data_json__ !== 'undefined' ?
__schedule_data_json__ : [];

// スケジュールを日付 ('YYYY-MM-DD') で検索するためのマップを作成
const schedulesByDate = scheduleData.reduce((acc, schedule) => {
    const dateKey = schedule.starting_day;
    if (!acc[dateKey]) {
        acc[dateKey] = [];
    }
    // スケジュール内容を追加
    acc[dateKey].push({
        item: schedule.item,
        content: schedule.content
    });
    return acc;
}, {});

    // 1. 月の情報を保持する変数 (現在の表示月)
    // 初回表示の月は、例えば今日の月を初期値とします
let currentYear = new Date().getFullYear();
let currentMonth = new Date().getMonth() + 1; // getMonth()は0から始まるため+1

const calendarTable = document.querySelector('.calendar-table');
const monthDisplay = document.getElementById('currentMonthDisplay');
const prevButton = document.getElementById('prevMonthBtn');
const nextButton = document.getElementById('nextMonthBtn');
const todayScheduleUl = document.getElementById('todayScheduleUl');
const weeks = ['日', '月', '火', '水', '木', '金', '土']
// 曜日を指定します。
const todayDate = new Date(); 
    // 任意の日付を設定する方法は、引数の中に数字をいれます ex:new Data(2020.11.11)
    // date = new Date();のnewはオブジェクトを初期化するキーワードです。

// 3. カレンダー描画関数
function renderCalendar(year, month) {
    // ヘッダーの年月を更新 (引数で渡された値を使用)
    document.querySelector('.calendar-area h2').innerHTML = `${year}年${month}月`;

    // 月の最初と最後の日を取得 (引数で渡された年月を使用)
    const startDate = new Date(year, month - 1, 1); 
    const endDate = new Date(year, month, 0); 

    const endDayCount = endDate.getDate(); // 月の末日
    const startDay = startDate.getDay();   // 月の最初の日の曜日

    let dayCount = 1; 
    let calendarHtml = '';

    // 曜日の行
    calendarHtml += '<thead><tr>';
    weeks.forEach(week => {
        calendarHtml += `<th>${week}</th>`;
    });
    calendarHtml += '</tr></thead>';

    // 日付部分
    calendarHtml += '<tbody class="date-number">';
    for (let j = 0; j < 6; j++) {
        calendarHtml += '<tr>';
        for (let i = 0; i < 7; i++) {
            if (j === 0 && i < startDay) {
                calendarHtml += `<td></td>`;
            } else if (dayCount > endDayCount) {
                calendarHtml += `<td></td>`;
            } else {
                // 日付のキーを作成 (YYYY-MM-DD形式)
                const dateKey = `${year}-${String(month).padStart(2, '0')}-${String(dayCount).padStart(2, '0')}`;
                
                // その日の予定を取得
                const daySchedules = schedulesByDate[dateKey] || [];
                
                // 予定のHTMLを生成
                let scheduleHtml = '';
                daySchedules.forEach((schedule) => {
                    const entryHtml = `<div class="schedule-entry ${schedule.item}">${schedule.content}</div>`;
                    scheduleHtml += entryHtml;
                });
                
                // 今日かどうかをチェック
                const isToday = year === todayDate.getFullYear() && 
                                month === todayDate.getMonth() + 1 && 
                                dayCount === todayDate.getDate();
                
                const todayClass = isToday ? ' class="today"' : '';

                // 今日のクラスと予定HTMLを追加
                calendarHtml += `<td${todayClass}><span>${dayCount}</span>${scheduleHtml}</td>`;
                dayCount++;
            }
        }
        calendarHtml += '</tr>';
        if (dayCount > endDayCount) break; 
    }
    calendarHtml += '</tbody>';

    // HTMLに描画
    calendarTable.innerHTML = calendarHtml;
}
// ここの'.calendar'が、HTMLの<table class="calendar-table"></table>にあたります。
// innerHTMLは、HTMLの中身を指定するプロパティです。
// なので、calendarHtmlの中身を、calendar-tableクラスの中に入れています。
// ちなみに、.calendar-tableはクラス指定なので、#calendar-tableにするとID指定になります。
// まとめると、HTMLの<table class="calendar-table"></table>の中に、calendarHtmlの中身を入れています。
// ちなみに、querySelectorは、CSSセレクタで要素を取得するメソッドです。
// 例えば、document.querySelector('#id名')や、document.querySelector('.class名')のように使います。

// 4. 月切り替え関数
function changeMonth(delta) {
    currentMonth += delta;

    if (currentMonth > 12) {
        currentMonth = 1;
        currentYear++;
    } else if (currentMonth < 1) {
        currentMonth = 12;
        currentYear--;
    }
    
    renderCalendar(currentYear, currentMonth); // 新しい年月でカレンダーを再描画
    // (補足) 今日・今週の予定リストもここで更新する関数を呼ぶ必要があります。
}

// 5. イベントリスナーの設定
prevButton.addEventListener('click', () => changeMonth(-1)); // -1: 前月へ
nextButton.addEventListener('click', () => changeMonth(1));  // 1: 次月へ

// 6. ページロード時にカレンダーを初期描画
document.addEventListener('DOMContentLoaded', () => {
    // index.htmlから渡された初期値（現在は2025年11月）を上書き
    renderCalendar(currentYear, currentMonth); 
});