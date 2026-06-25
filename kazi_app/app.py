from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import date, datetime
import calendar
import jpholiday

app = Flask(__name__)
DB_NAME = 'chores.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chores
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  last_done DATE NOT NULL)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    today = date.today()
    year = request.args.get('year', default=today.year, type=int)
    month = request.args.get('month', default=today.month, type=int)

    if month == 1:
        prev_year = year - 1
        prev_month = 12
    else:
        prev_year = year
        prev_month = month - 1

    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id, name, last_done FROM chores ORDER BY last_done ASC')
    rows = c.fetchall()
    conn.close()

    chores_list = []
    chores_by_date = {}

    for row in rows:
        last_done_date = date.fromisoformat(row[2])
        days_passed = (today - last_done_date).days
        chore = {
            'id': row[0],
            'name': row[1],
            'last_done': row[2],
            'days_passed': days_passed
        }
        chores_list.append(chore)

        if row[2] not in chores_by_date:
            chores_by_date[row[2]] = []
        chores_by_date[row[2]].append(chore)

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdatescalendar(year, month)

    calendar_data = []
    for week in month_days:
        week_data = []
        for day in week:
            holiday_name = jpholiday.is_holiday_name(day)
            week_data.append({
                'date': day,
                'day_num': day.day,
                'month': day.month,
                'iso': day.isoformat(),
                'is_holiday': holiday_name is not None,
                'holiday_name': holiday_name if holiday_name else '',
                'weekday': day.weekday()
            })
        calendar_data.append(week_data)

    month_name = datetime(year, month, 1).strftime('%B')

    return render_template('index.html', 
                           chores=chores_list,
                           calendar_data=calendar_data,
                           chores_by_date=chores_by_date,
                           today=today,
                           today_str=today.isoformat(),  # ★HTML側の初期値用に文字列を渡す
                           current_year=year,
                           current_month=month,
                           month_name=month_name,
                           prev_year=prev_year,
                           prev_month=prev_month,
                           next_year=next_year,
                           next_month=next_month)

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    last_done = request.form.get('last_done')  # ★画面から指定された日付を取得
    if not last_done:
        last_done = date.today().isoformat()

    if name:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('INSERT INTO chores (name, last_done) VALUES (?, ?)', (name, last_done))
        conn.commit()
        conn.close()
        
    # 現在表示していた年月を維持してリダイレクト
    year = request.form.get('year')
    month = request.form.get('month')
    if year and month:
        return redirect(url_for('index', year=year, month=month))
    return redirect(url_for('index'))

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    last_done = request.form.get('last_done')  # ★画面から指定された日付を取得
    if not last_done:
        last_done = date.today().isoformat()

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('UPDATE chores SET last_done = ? WHERE id = ?', (last_done, id))
    conn.commit()
    conn.close()
    
    # 現在表示していた年月を維持してリダイレクト
    year = request.form.get('year')
    month = request.form.get('month')
    if year and month:
        return redirect(url_for('index', year=year, month=month))
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM chores WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    # 現在表示していた年月を維持してリダイレクト
    year = request.form.get('year')
    month = request.form.get('month')
    if year and month:
        return redirect(url_for('index', year=year, month=month))
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)