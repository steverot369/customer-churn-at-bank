from flask import *
from database import *
from datetime import datetime
app.secret_key = 'your_secret_key' 
admin=Blueprint('admin',__name__)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="bank"
)

manager=Blueprint('manager',__name__)

@manager.route('/managerhome')
def managerhome():
    months = [
        'January', 'February', 'March', 'April',
        'May', 'June', 'July', 'August', 'September',
        'October', 'November', 'December'
    ]
    cursor = db.cursor()
    cursor.execute("SELECT MONTH(transaction_date), SUM(transaction_amount) FROM transactions GROUP BY MONTH(transaction_date)")
    data = cursor.fetchall()
    labels = []
    values = []
    for month in months:
        month_num = datetime.strptime(month, '%B').month
        found = False
        for row in data:
            if row[0] == month_num:
                labels.append(month)
                values.append(row[1])
                found = True
                break
        if not found:
            labels.append(month)
            values.append(0)
    cursor.execute("select sum(transaction_amount) from transactions")
    total_amount = cursor.fetchone()[0]
    cursor.execute("select employe_fname,employee_lname from employee where loginid='%s'"%(session['logid']))
    name = cursor.fetchall()
    # ===============feedbacks
    cursor.execute("select message,date from feedback order by date LIMIT 4")
    feedback_messages = cursor.fetchall()
    cursor = db.cursor() 
    return render_template('managerhome.html', labels=labels, values=values,total_amount=total_amount,name=name,feedback_messages=feedback_messages)
    
      
@manager.route('/publichome')
def publichome():
    session.clear()
    flash("Successfully logout...")
    return redirect(url_for('public.publichome'))
