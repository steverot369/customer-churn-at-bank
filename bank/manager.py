from flask import *
from database import *
from datetime import datetime
import joblib
import pandas as pd


model = joblib.load('churn_predict_model')
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


@manager.route('/managermanagehome')
def managermanagehome():
    return render_template('managermanagehome.html')




@manager.route('/managermanagecustomers',methods=['post','get'])
def managermanagecustomers():

    cursor = db.cursor()
    cursor.execute("select employe_fname,employee_lname,email from employee where loginid='%s'"%(session['logid']))
    name = cursor.fetchall()
    cursor.execute("SELECT * FROM customers where branch_id=(select branch_id from employee where employe_id='%s')"%(session['mid']))
    employees = cursor.fetchall()
    

    return render_template('managermanagecustomers.html',employees=employees,name=name)


# @manager.route('/managercustomerchurn/<customer_id>', methods=['GET', 'POST'])
# def managercustomerchurn(customer_id):
#     cursor = db.cursor()
#     cursor.execute("SELECT dob, msalary,state,date,active FROM customers WHERE cid='%s'" % customer_id)
#     customer_details = cursor.fetchall()
#     print(customer_details)
#     return render_template('managercustomerchurn.html', customer_id=customer_id, customer_details=customer_details)

@manager.route('/managercustomerchurn/<customer_id>', methods=['GET', 'POST'])
def managercustomerchurn(customer_id):
    cursor = db.cursor()
    cursor.execute("SELECT dob, msalary, state, date,gender active FROM customers WHERE cid='%s'" % customer_id)
    customer_details = cursor.fetchone()
    cursor.execute("SELECT count FROM bankproducts WHERE customer_id='%s'" % customer_id)
    customer_details1 = cursor.fetchone()
    cursor.execute("SELECT balance FROM savingsacc WHERE customer_id='%s'" % customer_id)
    customer_details2 = cursor.fetchone()
    # Calculate date and tenure
    dob = customer_details[0]
    msalary = customer_details[1]

    state = customer_details[2]
    

    joindate = customer_details[3]
    gender = customer_details[4]
    gender_value = 1 if gender == "Male" else 0

    current_date = datetime.today().date()
    dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
    age = (current_date - dob_date).days // 365
    today = datetime.today().date()
    date_date = datetime.strptime(joindate, "%Y-%m-%d").date()
    tenure = today.year - date_date.year - ((today.month, today.day) < (date_date.month, date_date.day))
    NumOfProducts = customer_details1[0]
    balance = customer_details2[0]


    # Pass date and tenure to the template
    return render_template('managercustomerchurn.html', customer_id=customer_id, customer_details=customer_details, age=age,state=state,tenure=tenure,msalary=msalary,NumOfProducts=NumOfProducts,balance=balance,gender_value=gender_value)

        
        