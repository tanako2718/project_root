// Python (Flask) から渡されたスケジュールデータ
// Jinja2の safe フィルターと tojson フィルターを使用して安全にJSONを埋め込み
// 実際のアプリケーションでは、この行はindex.htmlのテンプレート内で動作します。
// ここでは仮の値として空の配列を定義します。
const scheduleData = typeof __schedule_data_json__ !== 'undefined' ? JSON.parse(__schedule_data_json__) : [];

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

const weeks = ['日', '月', '火', '水', '木', '金', '土']
// 曜日を指定します。
const date = new Date(); 
// 任意の日付を設定する方法は、引数の中に数字をいれます ex:new Data(2020.11.11)
// date = new Date();のnewはオブジェクトを初期化するキーワードです。

const year = date.getFullYear()
// dateオブジェクトが持つ値から、年の値を取得します。

const month = date.getMonth()+1  
// 0 が年の最初の月を示すので、+1を記載します。+1を記載しないと今日が11月だった場合、10月と表示されてしまいます。

const  today = date.getDate()
// 今日の日付を取得します。
// ちなみに、getDateとgetDayの違いは、getDate：日を取得する getDay：曜日を０〜６の値で取得するです。曜日か日付かってことかな。

const startDate = new Date(year, month - 1, 1) 
// 月の最初の日を取得します。

const endDate = new Date(year, month,  0) 
// 月の最後の日を取得します。
// 何をやっているのかというと、日付に0を設定し、該当月の0日（つまり、前月末）にしてます。

const endDayCount = endDate.getDate()
// 月の末日

const startDay = startDate.getDay()
// 月の最初の日の曜日を取得

let dayCount = 1 
// 日にちのカウント 何日から始めるかを決めます。0にすると、カレンダーに0から始まります。

let calendarHtml = '' // HTMLを組み立てる変数
let scheduleHtml = '' // 予定をカレンダーに表示するための変数

calendarHtml += '<thead><tr>'
console.log(weeks)
weeks.forEach(week => {
    calendarHtml += `<th>${week}</th>`
    console.log(week)
})
calendarHtml += '</tr></thead>'
// ここまでで、曜日の部分を作成しています。

calendarHtml += '<tbody class="date-number">'
for (let j = 0; j < 6; j++) {
    calendarHtml += '<tr>'
    for (let i = 0; i < 7; i++) {
        if (j === 0 && i < startDay) {
            calendarHtml += `<td></td>`
        } else if (dayCount > endDayCount) {
            calendarHtml += `<td></td>`
        } else if (dayCount === today) {
            calendarHtml += `<td><span>${dayCount}</span></td>`
            dayCount++
        } else {
            calendarHtml += `<td><span>${dayCount}</span></td>`
            dayCount++
        }
    }
    calendarHtml += '</tr>'
}
calendarHtml += '</tbody>'

console.log(calendarHtml)

document.querySelector('.calendar-table').innerHTML = calendarHtml
document.querySelector('.schedule-entry').innerHTML = scheduleHtml
// ここの'.calendar'が、HTMLの<table class="calendar-table"></table>にあたります。
// innerHTMLは、HTMLの中身を指定するプロパティです。
// なので、calendarHtmlの中身を、calendar-tableクラスの中に入れています。
// ちなみに、.calendar-tableはクラス指定なので、#calendar-tableにするとID指定になります。
// まとめると、HTMLの<table class="calendar-table"></table>の中に、calendarHtmlの中身を入れています。
// ちなみに、querySelectorは、CSSセレクタで要素を取得するメソッドです。
// 例えば、document.querySelector('#id名')や、document.querySelector('.class名')のように使います。
