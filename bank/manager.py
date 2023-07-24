from flask import *
from database import *
import uuid
from datetime import datetime,timedelta
import datetime
import joblib
import pandas as pd
import random
import os
# model_path = os.path.join('C:', 'mca project 2023', 'BankManagement', 'bank', 'churn_predict_model')
model = joblib.load('C:/mca project 2023/BankManagement/bank/churn_predict_model')
# # model = joblib.load('churn_predict_model')
# C:\mca project 2023\BankManagement\bank\churn_predict_model
app.secret_key = 'your_secret_key' 
admin=Blueprint('admin',__name__)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="bank"
)

manager=Blueprint('manager',__name__)

# @manager.route('/managerhome')
# def managerhome():
#     months = [
#         'January', 'February', 'March', 'April',
#         'May', 'June', 'July', 'August', 'September',
#         'October', 'November', 'December'
#     ]
#     cursor = db.cursor()
#     cursor.execute("SELECT MONTH(transaction_date), SUM(transaction_amount) FROM transactions GROUP BY MONTH(transaction_date)")
#     data = cursor.fetchall()
#     labels = []
#     values = []
#     for month in months:
#         month_num = datetime.datetime.strptime(month, '%B').month
#         found = False
#         for row in data:
#             if row[0] == month_num:
#                 labels.append(month)
#                 values.append(row[1])
#                 found = True
#                 break
#         if not found:
#             labels.append(month)
#             values.append(0)
#     cursor.execute("select sum(transaction_amount) from transactions")
#     total_amount = cursor.fetchone()[0]
#     cursor.execute("select employe_fname,employee_lname,email from employee where loginid='%s'"%(session['logid']))
#     name = cursor.fetchall()
#     # ===============feedbacks
#     cursor.execute("select message,date from feedback order by date LIMIT 4")
#     feedback_messages = cursor.fetchall()
#     cursor = db.cursor() 
#     return render_template('managerhome.html', labels=labels, values=values,total_amount=total_amount,name=name,feedback_messages=feedback_messages)
@manager.route('/managerhome')
def managerhome():
    months = [
        'January', 'February', 'March', 'April',
        'May', 'June', 'July', 'August', 'September',
        'October', 'November', 'December'
    ]
    cursor = db.cursor()
    cursor.execute("SELECT MONTH(date_time), SUM(amount) FROM transaction GROUP BY MONTH(date_time)")
    data = cursor.fetchall()
    labels = []
    values = []
    for month in months:
        month_num = datetime.datetime.strptime(month, '%B').month
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
    cursor.execute("select employe_fname,employee_lname,email,image from employee where loginid='%s'"%(session['logid']))
    name = cursor.fetchall()
    cursor.fetchall()
    cursor.execute("select branch_id from employee where employe_id='%s'"%(session['mid']))
    branch_id=cursor.fetchone()[0]




    cursor.execute("""
        SELECT note_type, SUM(count) AS total_count
        FROM notescount
        GROUP BY note_type
        ORDER BY note_type DESC;
    """)

    # Fetch all rows from the result
    notes = cursor.fetchall()

    
   





    # ===============feedbacks
    cursor.execute("SELECT f.messages, f.date_time, c.photo,c.fname,c.lname FROM feedbacks f INNER JOIN customers c ON f.customer_id = c.cid ORDER BY f.date_time LIMIT 3")

    feedback_messages = cursor.fetchall()
 
    cursor = db.cursor()
    cursor.execute("SELECT c.fname,c.lname,c.photo,tt.amount,tt.date_time,tt.t_type,tt.t_no FROM customers c,transaction tt where c.cid=tt.customer_id and tt.t_type='online' and tt.branch_id='%s' LIMIT 4"%(branch_id))
    online_transaction=cursor.fetchall()
    cursor.execute("SELECT c.fname,c.lname,tt.t_no,tt.t_type,tt.amount,tt.date_time FROM customers c,transaction tt where c.cid=tt.customer_id and tt.branch_id='%s'"%(branch_id))
    transaction=cursor.fetchall()

    current_month_start = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month_end = current_month_start.replace(day=1, month=current_month_start.month + 1) - timedelta(days=1)

    current_month_query = "SELECT SUM(amount) FROM transaction WHERE branch_id='%s' and  date_time BETWEEN %s AND %s"
    cursor.execute(current_month_query, (branch_id,current_month_start, current_month_end))
    current_month_result = cursor.fetchone()
    current_month_amount = current_month_result[0] if current_month_result[0] is not None else 0

    previous_month_query = "SELECT SUM(amount) FROM transaction WHERE branch_id='%s' and date_time BETWEEN %s AND %s"
    cursor.execute(previous_month_query, (branch_id, current_month_start - timedelta(days=30), current_month_start - timedelta(days=1)))
    previous_month_result = cursor.fetchone()
    previous_month_amount = previous_month_result[0] if previous_month_result[0] is not None else 0

    percentage_change = ((current_month_amount - previous_month_amount) / previous_month_amount) * 100 if previous_month_amount != 0 else 0
    percentage_change = min(percentage_change, 100)  # Limit the percentage change to 100
    percentage_change = round(percentage_change, 2)


    current_year = datetime.datetime.now().year
    previous_year = current_year - 1

    current_year_query = "SELECT COUNT(*) FROM customers WHERE branch_id='%s' and YEAR(date) = %s"
    cursor.execute(current_year_query, (branch_id, current_year,))
    current_year_result = cursor.fetchone()
    current_year_count = current_year_result[0] if current_year_result[0] is not None else 0

    previous_year_query = "SELECT COUNT(*) FROM customers WHERE branch_id='%s' and YEAR(date) = %s"
    cursor.execute(previous_year_query, (branch_id, previous_year,))
    previous_year_result = cursor.fetchone()
    previous_year_count = previous_year_result[0] if previous_year_result[0] is not None else 0

    customer_percentage_change = ((current_year_count - previous_year_count) / previous_year_count) * 100 if previous_year_count != 0 else 0
    customer_percentage_change = min(customer_percentage_change, 100)  # Limit the percentage change to 100
    customer_percentage_change = round(customer_percentage_change, 2)  # Round to two decimal places

   

    current_month_query1 = "SELECT COUNT(savings_id) FROM savingsacc WHERE branch_id='%s' and acc_started_date BETWEEN %s AND %s"
    cursor.execute(current_month_query1, (branch_id, current_month_start, current_month_end))
    current_month_result = cursor.fetchone()
    print("======current_month_result==========",current_month_result)
    current_month_balance = current_month_result[0] if current_month_result[0] is not None else 0

    previous_month_query1 = "SELECT COUNT(savings_id) FROM savingsacc WHERE branch_id='%s' and acc_started_date  BETWEEN %s AND %s"
    cursor.execute(previous_month_query1, (branch_id, current_month_start - timedelta(days=30), current_month_start - timedelta(days=1)))
    previous_month_result = cursor.fetchone()
    print("=======previous_month_result=========",previous_month_result)
    previous_month_balance = previous_month_result[0] if previous_month_result[0] is not None else 0

    account_percentage_change = ((current_month_balance - previous_month_balance) / previous_month_balance) * 100 if previous_month_balance != 0 else 0
    account_percentage_change = round(account_percentage_change, 2)


    # for loan account
    current_month_query2 = "SELECT COUNT(loan_id) FROM loanacc WHERE branch_id='%s' and date_issued BETWEEN %s AND %s"
    cursor.execute(current_month_query2, (branch_id, current_month_start, current_month_end))
    current_month_result = cursor.fetchone()
    print("======current_month_result==========",current_month_result)
    current_month_balance1 = current_month_result[0] if current_month_result[0] is not None else 0

    previous_month_query2 = "SELECT COUNT(loan_id) FROM loanacc WHERE branch_id='%s' and date_issued BETWEEN %s AND %s"
    cursor.execute(previous_month_query2, (branch_id, current_month_start - timedelta(days=30), current_month_start - timedelta(days=1)))
    previous_month_result = cursor.fetchone()
    print("=======previous_month_result=========",previous_month_result)
    previous_month_balance1 = previous_month_result[0] if previous_month_result[0] is not None else 0

    loan_account_percentage_change = ((current_month_balance1 - previous_month_balance1) / previous_month_balance1) * 100 if previous_month_balance1 != 0 else 0
    loan_account_percentage_change = round(loan_account_percentage_change, 2)

    cursor.execute("select count(*) from customers where branch_id='%s'"%(branch_id))
    customer_count=cursor.fetchone()[0]
    cursor.execute("select count(*) from employee where branch_id='%s' and employee='clerk'"%(branch_id))
    employee_count=cursor.fetchone()[0]


    cursor.execute("""
    SELECT l.acc_type, l.acc_no, l.date_issued, c.fname, c.lname
    FROM loanacc l, customers c
    WHERE l.customer_id = c.cid
    UNION
    SELECT s.acc_type, s.acc_no, s.acc_started_date, c.fname, c.lname
    FROM savingsacc s, customers c
    WHERE s.customer_id = c.cid
    UNION
    SELECT d.acc_type, d.acc_no, d.deposit_date, c.fname, c.lname
    FROM depositacc d, customers c
    WHERE d.customer_id = c.cid AND acc_status='active'
    AND d.branch_id = (SELECT branch_id FROM employee WHERE employe_id = %s)
    """, (session['mid'],))

    row_count=cursor.fetchall()
    account_count = cursor.rowcount

    query = "SELECT COUNT(*) FROM complaints where reply='0'"
   
    cursor.execute(query)
    count = cursor.fetchone()[0]
    print("max date=",query)

    current_datetime=datetime.datetime.now()
    current_date = current_datetime.date()

    print('cureetn date',current_date)
    cursor.execute("SELECT messages,date FROM bank_messages WHERE message_type='bank' AND DATE(date) = '%s' AND (user_type='employee' OR user_type='manager') AND branch_id='%s' ORDER BY date DESC LIMIT 3"% (current_date,branch_id))
    bank_messages = cursor.fetchall()

    cursor.execute("SELECT messages,date,message_type FROM bank_messages where message_type='credit' AND (user_type='employee' OR user_type='manager') AND DATE(date) = '%s' ORDER BY date DESC LIMIT 3"%(current_date))
    bank_messages1 = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM bank_messages WHERE (message_type='bank' OR message_type='credit') AND DATE(date) = '%s' AND (user_type='employee' OR user_type='manager') AND branch_id='%s'" % (current_date,branch_id))
    messages_count = cursor.fetchone()[0]


    if 'count_removed' in session:
        session.pop('count_removed')  # Remove the 'count_removed' flag from session
    
    return render_template('managerhome.html', 
    labels=labels, values=values,total_amount=total_amount,name=name,feedback_messages=feedback_messages,count=count,online_transaction=online_transaction,notes=notes,
    transaction=transaction, current_month_amount=current_month_amount,
     previous_month_amount=previous_month_amount, percentage_change=percentage_change,
     current_year_count=current_year_count, previous_year_count=previous_year_count, customer_percentage_change=customer_percentage_change, 
     current_month_balance=current_month_balance, previous_month_balance=previous_month_balance, account_percentage_change=account_percentage_change,
     current_month_balance1=current_month_balance1, previous_month_balance1=previous_month_balance1, loan_account_percentage_change=loan_account_percentage_change,
     customer_count=customer_count,employee_count=employee_count,bank_messages=bank_messages,
     messages_count=messages_count,account_count=account_count,bank_messages1=bank_messages1)
    
      
@manager.route('/publichome')
def publichome():
    session.clear()
    flash("Successfully logout...")
    return redirect(url_for('public.publichome'))


@manager.route('/setusername',methods=['POST','GET'])
def setusername():
    cursor=db.cursor()
    cursor.execute("select employe_fname,employee_lname,email,image from employee where loginid='%s'"%(session['logid']))
    name12 = cursor.fetchall()
    cursor.execute("select uname from login")
    uname=[row[0] for row in cursor.fetchall()]
    cursor.execute("select count,login_type from login where loginid='%s'"%(session['logid']))
    logindetails=cursor.fetchone()
    count=logindetails[0]
    logintype=logindetails[1]

  
    cursor.fetchall()

    if 'add' in request.form:
        username=request.form['username']
        password=request.form['password']
        cursor.execute("UPDATE login SET uname='%s', password='%s', count='yes' WHERE loginid='%s'" % (username, password, session['logid']))

        flash("successfuly change username and password")
        return redirect(url_for('public.login'))

    return render_template('setusername.html',uname=uname,count=count,name12=name12,logintype=logintype)

@manager.route('/managermanagehome')
def managermanagehome():
    cursor=db.cursor()
    cursor.execute("select employe_fname,employee_lname,email,image from employee where loginid='%s'"%(session['logid']))
    name12 = cursor.fetchall()
    return render_template('managermanagehome.html',name12=name12)





@manager.route('/managermanagecustomers',methods=['post','get'])
def managermanagecustomers():

    cursor = db.cursor()
    cursor.execute("select employe_fname,employee_lname,email,image from employee where loginid='%s'"%(session['logid']))
    name12 = cursor.fetchall()
    current_date = datetime.datetime.now()

# Calculate the date two years ago from the current date
    two_years_ago = current_date - datetime.timedelta(days=365*2)
    two_years_ago_str = two_years_ago.strftime('%Y-%m-%d')
    cursor.execute("SELECT * FROM customers WHERE branch_id=(SELECT branch_id FROM employee WHERE employe_id='%s') AND date <= '%s' and active='1'" % (session['mid'], two_years_ago_str))
    employees = cursor.fetchall()
    date=datetime.datetime.now()
    if 'add' in request.form:
       
        messages=request.form['messages']
        customer_id=request.form['customer_id']
        min_allowed_time =  date - timedelta(hours=1)
        cursor.execute("SELECT MAX(date) FROM bank_messages WHERE customer_id = %s", (customer_id,))
        last_submission_time = cursor.fetchone()[0]
        cursor.execute("select branch_id from customers where cid='%s'" % customer_id)
        details=cursor.fetchone()
        print(details)
        branch_id=details[0]
        
        if last_submission_time is None or last_submission_time < min_allowed_time:
            bank_messages="INSERT INTO bank_messages(customer_id,branch_id,messages,user_type,messsage_type,date)  VALUES ( %s, %s, %s,'customer','bank',%s)"
            bank_messages_values = (customer_id, branch_id,messages,date)
            cursor.execute(bank_messages, bank_messages_values)
            # cursor.execute("SELECT * FROM customers where branch_id=(select branch_id from employee where employe_id='%s')"%(session['mid']))
            # employees = cursor.fetchall()
            flash("successfully send notification")
        else:
            print('send after 1 hoursuccess')

    if "action" in request.args:
        action=request.args['action']
       
        id=request.args['delete_id']
    else:
        action="none"

        
    if action=="reject":
       
        
        cursor.execute("update customers set active='0' where loginid='%s'"%(id))
        cursor.execute("update login set status='reject' where loginid='%s'"%(id))

        
        flash('Rejected successfully !')
        return redirect(url_for('manager.managermanagecustomers'))
        
    

    return render_template('managermanagecustomers.html',employees=employees,name12=name12)



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
    cursor.execute("select employe_fname,employee_lname,email,image from employee where loginid='%s'"%(session['logid']))
    name12 = cursor.fetchall()
    cursor.execute("SELECT dob, msalary, state, date,gender,active,fname,lname FROM customers WHERE cid='%s'" % customer_id)
    customer_details = cursor.fetchone()
    cursor.execute("SELECT count FROM bankproducts WHERE customer_id='%s'" % customer_id)
    customer_details1 = cursor.fetchone()
    cursor.execute("SELECT customer_id, SUM(balance) FROM savingsacc WHERE customer_id='%s' GROUP BY customer_id" % customer_id)
    customer_balances = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(customer_id) FROM transaction WHERE customer_id='%s'" % customer_id)
    customer_details3 = cursor.fetchone()


    # Calculate date and tenure
    dob = customer_details[0]
    msalary = customer_details[1]
    f_name = customer_details[6]
    l_name = customer_details[7]
    state = customer_details[2]

    cursor.execute("SELECT status FROM credit_card WHERE customer_id='%s'" % customer_id)
    customer_details4 = cursor.fetchone()

    try:
        credit_status = customer_details4[0]
        credit_status = 1 if credit_status == "approve" else 0
    except TypeError:
        credit_status = 0  # Default value if customer_details4 is None or IndexError occurs

    print("credit==================", credit_status)


    cursor.execute("SELECT sum(penality_count) FROM loanacc WHERE customer_id='%s'" % (customer_id))
    penality_result = cursor.fetchone()

    if penality_result:
        penality = penality_result[0]
    else:
        penality = 0

    Geography_Germany = customer_details[2]
    if(Geography_Germany == 'kerala'):
        Geography_Germany = 1
        Geography_Spain= 0
        Geography_France = 0
                
    elif(Geography_Germany == 'karnadaka'):
        Geography_Germany = 0
        Geography_Spain= 1
        Geography_France = 0
        
    else:
        Geography_Germany = 0
        Geography_Spain= 0
        Geography_France = 1
        

    joindate = customer_details[3]
    gender = customer_details[4]
    gender_value = 1 if gender == "male" else 0

    current_date = datetime.datetime.now().date()
    dob_date = datetime.datetime.strptime(dob, "%Y-%m-%d").date()
    age = (current_date - dob_date).days // 365
    today = datetime.datetime.now().date()
    date_date = datetime.datetime.strptime(joindate, "%Y-%m-%d").date()
    tenure = today.year - date_date.year - ((today.month, today.day) < (date_date.month, date_date.day))
    NumOfProducts = customer_details1[0]
    balances = customer_balances[1]
    # balances = [balance[1] for balance in customer_balances]
    IsActiveMember = customer_details3[0]
    IsActiveMembervalue = 1 if IsActiveMember >= 20 else 0
    credit_score = 0

        # Age factor
    if age >= 18 and age < 21:
        credit_score += 120
    elif age >= 21 and age < 25:
        credit_score += 150
    elif age >= 25 and age < 30:
        credit_score += 175
    elif age >= 30:
        credit_score += 300
    print("credit score on age=",credit_score)

        # Loan penalty factor
    if penality is not None and penality > 0:
        
        credit_score -= 100
    print("credit score on penality=",credit_score)

        # Loan penalty factor


        # Active member factor
    if NumOfProducts >= 1:
        credit_score += 20
        if NumOfProducts >= 2:
            credit_score += 50
        if NumOfProducts >= 3:
            credit_score += 75
        if NumOfProducts >= 4:
            credit_score += 100
        print("credit score on number of preoducts=",credit_score)

        # NumOfProducts factor
        # Active member factor
    if IsActiveMember > 1:
        credit_score += 50
        if IsActiveMember > 10:
            credit_score += 100
        if IsActiveMember > 20:
            credit_score += 150
        print("credit score on transaction=",credit_score)

        # Limit credit score to a maximum of 1000
    credit_score = min(credit_score, 1000)

        # Print the credit score
    print("Credit Score:", credit_score)


    if 'add' in request.form:
        CreditScore=int(request.form['credit_score'])
        Age = int(request.form['age'])
        Tenure = int(request.form['tenure'])
        Balance = float(request.form['balance'])
        NumOfProducts = int(request.form['num_of_products'])
        HasCrCard = int(request.form['has_cr_card'])
        IsActiveMember = int(request.form['is_active_member'])
        EstimatedSalary = float(request.form['estimated_salary'])
        Geography_Germany = int(request.form['geography_germany'])
        Geography_Spain = int(request.form['geography_spain'])
        Gender = int(request.form['gender'])
        cursor.execute("SELECT dob, msalary, state, date,gender,active,fname,lname FROM customers WHERE cid='%s'" % customer_id)
        customer_details = cursor.fetchone()
        cursor.execute("SELECT count FROM bankproducts WHERE customer_id='%s'" % customer_id)
        customer_details1 = cursor.fetchone()
        cursor.execute("SELECT customer_id, SUM(balance) FROM savingsacc WHERE customer_id='%s' GROUP BY customer_id" % customer_id)
        customer_balances = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(customer_id) FROM transaction WHERE customer_id='%s'" % customer_id)
        customer_details3 = cursor.fetchone()
        cursor.execute("SELECT branch_id FROM customers WHERE cid='%s'" % customer_id)
        branch_id = cursor.fetchone()[0]
        # Calculate date and tenure
        dob = customer_details[0]
        msalary = customer_details[1]
        state = customer_details[2]
        cursor.execute("SELECT status FROM credit_card WHERE customer_id='%s'" % customer_id)
        customer_details4 = cursor.fetchone()
        

        if customer_details4 is not None:
            credit_status = 1 if customer_details4[0] == "approve" else 0

        cursor.execute("SELECT sum(penality_count) FROM loanacc WHERE customer_id='%s'" %(customer_id))
        penality_result = cursor.fetchone()

        if penality_result:
            penality = penality_result[0]
        else:
            penality = 0

        Geography_Germany = customer_details[2]
        if(Geography_Germany == 'kerala'):
            Geography_Germany = 1
            Geography_Spain= 0
            Geography_France = 0
                    
        elif(Geography_Germany == 'karnadaka'):
            Geography_Germany = 0
            Geography_Spain= 1
            Geography_France = 0
            
        else:
            Geography_Germany = 0
            Geography_Spain= 0
            Geography_France = 1
            

        joindate = customer_details[3]
        gender = customer_details[4]
        gender_value = 1 if gender == "male" else 0

        current_date = datetime.datetime.now().date()
        dob_date = datetime.datetime.strptime(dob, "%Y-%m-%d").date()
        age = (current_date - dob_date).days // 365
        today = datetime.datetime.now().date()
        date_date = datetime.datetime.strptime(joindate, "%Y-%m-%d").date()
        tenure = today.year - date_date.year - ((today.month, today.day) < (date_date.month, date_date.day))
        NumOfProducts = customer_details1[0]
        balances = customer_balances[1]
        # balances = [balance[1] for balance in customer_balances]
        IsActiveMember = customer_details3[0]
        print("transaction=================",IsActiveMember)
        IsActiveMembervalue = 1 if IsActiveMember >= 20 else 0
        credit_score = 0

        # Age factor
        if age >= 18 and age < 21:
            credit_score += 120
        elif age >= 21 and age < 25:
            credit_score += 150
        elif age >= 25 and age < 30:
            credit_score += 175
        elif age >= 30:
            credit_score += 300
            print("credit score on age=",credit_score)
        # Loan penalty factor
        if penality is not None and penality > 0:
            credit_score -= 100
        print("credit score on penality=",credit_score)

       

        # Active member factor
        if IsActiveMember > 1:
            credit_score += 50
            if IsActiveMember > 10:
                credit_score += 100
            if IsActiveMember > 20:
                credit_score += 150
            print("credit score on transaction=",credit_score)


        # NumOfProducts factor
        if NumOfProducts >= 1:
            credit_score += 20
            if NumOfProducts >= 2:
                credit_score += 50
            if NumOfProducts >= 3:
                credit_score += 75
            if NumOfProducts >= 4:
                credit_score += 100
            print("credit score on number of preoducts=",credit_score)

        # Limit credit score to a maximum of 1000
        credit_score = min(credit_score, 950)

        # Print the credit score
        print("Credit Score:", credit_score)
 
        prediction_data = pd.DataFrame({
                'CreditScore': [CreditScore],
                'Age': [Age],
                'Tenure': [Tenure],
                'Balance': [Balance],
                'NumOfProducts': [NumOfProducts],
                'HasCrCard': [HasCrCard],
                'IsActiveMember': [IsActiveMember],
                'EstimatedSalary': [EstimatedSalary],
                'Geography_Germany': [Geography_Germany],
                'Geography_Spain': [Geography_Spain],
                'Gender_Male': [Gender]
            })

        prediction = model.predict(prediction_data)
        probability = model.predict_proba(prediction_data)[0][1] * 100
        stay_probability = 100 - probability
      

        credit=CreditScore
        if prediction == 1:
            check_existing_customer = "SELECT customer_id FROM churn_customers WHERE customer_id = %s"
            cursor.execute(check_existing_customer, (customer_id,))
            existing_customer = cursor.fetchone()

            if existing_customer is None:
                churn = "INSERT INTO churn_customers (customer_id, branch_id, leave_or_not) VALUES (%s, %s, 'will leave')"
                churn_values = (customer_id, branch_id)
                cursor.execute(churn, churn_values)
                # Add code for further processing if the insert was successful
            else:
                # Add code to handle the case when a customer with the same ID already exists
                print("no value is fetch")
            reason1 = "no data"
            reason2 = "no data"
            reason3 = "no data"
            reason4 = "no data"
            reason5 = "no data"
            # Check conditions and update reason
            if Tenure < 2:
                reason1 = "Low Tenure"
            if CreditScore < CreditScore:
                reason2 = "Low Credit Score"
            if IsActiveMembervalue == 0:
                reason3 = "Inactive Customer"
            if NumOfProducts < 4:
                reason4 = "High Number of Bank Products"
            if HasCrCard == 0:
                reason5 = "No Credit Card"
           

            return render_template('predictionresult.html', prediction_text="The Customer will leave the bank",
                                probability=probability, stay_probability=stay_probability,
                                customer_id=customer_id, customer_details=customer_details, age=age,
                                Geography_Germany=Geography_Germany, Geography_Spain=Geography_Spain,
                                tenure=tenure, msalary=msalary, NumOfProducts=NumOfProducts, balances=balances,
                                gender_value=gender_value, IsActiveMembervalue=IsActiveMembervalue,
                                credit_score=credit_score, f_name=f_name, l_name=l_name, state=state,
                                credit_status=credit_status, reason1=reason1,reason2=reason2,reason3=reason3,reason4=reason4,reason5=reason5,name12=name12)
        else:
            return render_template('predictionresult.html', prediction_text="The Customer will not leave the bank",
                                probability=stay_probability, stay_probability=probability,
                                customer_id=customer_id, customer_details=customer_details, age=age,
                                Geography_Germany=Geography_Germany, Geography_Spain=Geography_Spain,
                                tenure=tenure, msalary=msalary, NumOfProducts=NumOfProducts, balances=balances,
                                gender_value=gender_value, IsActiveMembervalue=IsActiveMembervalue,
                                credit_score=credit_score, f_name=f_name, l_name=l_name, state=state,
                                credit_status=credit_status,name12=name12)


    # Pass date and tenure to the template
    return render_template('managercustomerchurn.html', customer_id=customer_id, customer_details=customer_details, age=age,Geography_Germany=Geography_Germany,Geography_Spain=Geography_Spain,tenure=tenure,msalary=msalary,NumOfProducts=NumOfProducts,balances=balances,gender_value=gender_value,IsActiveMembervalue=IsActiveMembervalue,credit_score=credit_score,f_name=f_name,l_name=l_name,state=state,credit_status=credit_status)

@manager.route('/customerchurnprediction', methods=['POST'])
def customerchurnprediction():
    cursor=db.cursor()
    cursor.execute("select employe_fname,employee_lname,email,image from employee where loginid='%s'"%(session['logid']))
    name12 = cursor.fetchall()
    if 'add' in request.form:
        creditscore=request.form['credit_score']
        age = request.form['age']
        tenure = request.form['tenure']
        balance = request.form['balance']
        num_of_products = request.form['num_of_products']
        has_cr_card = request.form['has_cr_card']
        is_active_member = request.form['is_active_member']
        estimated_salary = request.form['estimated_salary']
        geography_germany = request.form['geography_germany']
        geography_spain = request.form['geography_spain']
        gender = request.form['gender']
        prediction_data = pd.DataFrame({
                'CreditScore': [creditscore],
                'Age': [age],
                'Tenure': [tenure],
                'Balance': [balance],
                'NumOfProducts': [num_of_products],
                'HasCrCard': [has_cr_card],
                'IsActiveMember': [is_active_member],
                'EstimatedSalary': [estimated_salary],
                'Geography_Germany': [geography_germany],
                'Geography_Spain': [geography_spain],
                'Gender_Male': [gender]
            })

        prediction = model.predict(prediction_data)
        probability = model.predict_proba(prediction_data)[0][1] * 100
        stay_probability = 100 - probability
        if prediction == 1:
            return render_template('predictionresult.html', prediction_text="The Customer will leave the bank",
                                   probability=probability, stay_probability=stay_probability,name12=name12)
        else:
            return render_template('predictionresult.html', prediction_text="The Customer will not leave the bank",
                                   probability=stay_probability, stay_probability=probability,name12=name12)
    return render_template('customerchurnprediction.html')





@manager.route('/managerviewloanacc',methods=['post','get'])
def clerkviewloanacc():

    cursor = db.cursor()
    cursor.execute("select employe_fname,employee_lname,email from employee where loginid='%s'"%(session['logid']))
    name12 = cursor.fetchall()
    cursor.execute("SELECT c.fname,c.lname,l.acc_no,l.ifsccode,l.interst_amt,l.interest_rate,l.issued_amount,l.remaing_amount,l.acc_status,l.date_interest,l.loan_type FROM customers c,loanacc l where c.cid=l.customer_id and l.branch_id=(select branch_id from employee where employe_id='%s')"%(session['mid']))
    employees = cursor.fetchall()
    date = datetime.datetime.now()
    formatted_date = date.strftime("%d-%m-%y")
    return render_template('managerviewloanacc.html',employees=employees,name12=name12,formatted_date=formatted_date)
    

@manager.route('/managerviewtransaction',methods=['post','get'])
def managerviewtransaction():

    cursor = db.cursor()
    cursor.execute("select employe_fname,employee_lname,email from employee where loginid='%s'"%(session['logid']))
    name12 = cursor.fetchall()
    cursor.execute("SELECT t.t_no,t.t_type,t.amount,t.date_time,c.fname,c.lname,s.acc_no from transaction t,customers c,savingsacc s where t.customer_id=c.cid AND t.customer_id=s.customer_id AND t.branch_id=(select branch_id from employee where employe_id='%s')"%(session['mid']))
    employees = cursor.fetchall()
    date = datetime.datetime.now().date()
    formatted_date = datetime.datetime.strftime(date,"%d-%m-%y")
    return render_template('managerviewtransaction.html',employees=employees,name12=name12,formatted_date=formatted_date)
        
          
@manager.route('/managerviewcreditcard')
def managerviewcreditcard():
    cursor = db.cursor()
    cursor.execute("select employe_fname,employee_lname,email,image from employee where loginid='%s'"%(session['logid']))
    name12 = cursor.fetchall()
    # cursor.execute("SELECT card_name, job_type, c_name, c_location, m_salary, file1, file2, file3, date, status FROM o_credit_card_request WHERE branch_id = (SELECT branch_id FROM employee WHERE employe_id = '%s')" % (session['mid']))
    cursor.execute("SELECT c.card_name, c.job_type, c.c_name, c.c_location, c.m_salary, c.file1, c.file2, c.file3, c.date, c.status, cu.fname, cu.lname, cu.phone,c.o_request_id FROM o_credit_card_request c INNER JOIN customers cu ON c.customer_id = cu.cid WHERE c.branch_id = (SELECT branch_id FROM employee WHERE employe_id = '%s')"% (session['mid']))
    credit_card = cursor.fetchall()


    if "action" in request.args:
        action=request.args['action']
       
        id=request.args['id']
    else:
        action="none"
    if action=="approve":
        cursor.execute("SELECT m_salary, job_type,card_name FROM o_credit_card_request WHERE branch_id=(SELECT branch_id FROM employee WHERE employe_id='%s')" % (session['mid']))
        credit_request = cursor.fetchone()
        msalary = credit_request[0]
        jobtype = credit_request[1]
        card_name = credit_request[2]

        cursor.fetchall()
        cursor.execute("SELECT customer_id FROM o_credit_card_request WHERE branch_id = (SELECT branch_id FROM employee WHERE employe_id = '%s') AND o_request_id='%s'"% (session['mid'],id))
        customer_details = cursor.fetchone()
        cid=customer_details[0]
        cursor.execute("SELECT cid, branch_id, dob FROM customers WHERE branch_id=(SELECT branch_id FROM employee WHERE employe_id='%s') AND cid='%s'" % (session['mid'],cid))
        result = cursor.fetchone()
        # cid = result[0]
        branch_id = result[1]
        dob = result[2]

        # Fetch all results before executing the next query
        cursor.fetchall()

        date = datetime.datetime.now().date()
        date1 = datetime.datetime.now()

        dob_date = datetime.datetime.strptime(dob, "%Y-%m-%d").date()
        age = (date - dob_date).days // 365

        expiry_date = (datetime.datetime.now() + datetime.timedelta(days=365 * 20)).date()

        cursor.execute("SELECT COUNT(customer_id) FROM transaction WHERE customer_id='%s'" % (cid))
        transaction = cursor.fetchone()[0]
        cursor.execute("SELECT sum(penality_count) FROM loanacc WHERE customer_id='%s'" % (cid))
        penality_result = cursor.fetchone()

        

        if penality_result:
            penality = penality_result[0]
        else:
            penality = 0
        if age >= 18:
            credit = 5000
            if msalary >= 5000:
                credit += 5000
            if transaction > 2:
                credit += 5000
            if age >= 21:
                credit += 3000
            if msalary >= 10000:
                credit += 3000
            if transaction > 5:
                credit += 3000
            if age >= 25:
                credit += 2000
            if msalary >= 15000:
                credit += 2000
            if transaction > 10:
                credit += 2000
            if age >= 30:
                credit += 1000
            if msalary >= 20000:
                credit += 1000
            if transaction > 15:
                credit += 1000
            print("job=",credit)
        # Additional credit based on job type
        if jobtype == "doctor":
            credit += 5000
        elif jobtype == "defense":
            credit += 4000
        elif jobtype == "pensioner":
            credit += 3000
        else:
            credit += 2000
        print("jobtype=",credit)
        if penality is not None and penality > 0:
            credit -= penality * 1000
            
            print("penality=",credit)
        total_limit = credit


        

        
        debit_card_no = str(random.randint(1000000000000000, 9999999999999999))
        cv = str(random.randint(100, 999))
        expiry_date = (datetime.datetime.now() + datetime.timedelta(days=365 * 20)).date()
        cursor.execute("SELECT count(customer_id) FROM transaction WHERE customer_id='%s'"%(cid))
        transaction = cursor.fetchone()[0]
        
       
        cursor.fetchall()
        cursor.execute("update o_credit_card_request set status='Active' where o_request_id='%s'"%(id))
        credit_card="INSERT INTO credit_card(customer_id,branch_id,card_name,card_no,card_limit,cv,expiry_date,j_date,status)  VALUES (%s, %s, %s, %s,%s, %s,%s,%s,'approve')"
        credit_card_values = (cid, branch_id,card_name, debit_card_no, total_limit,cv, expiry_date,date)
        cursor.execute(credit_card, credit_card_values)
        messages_bank=f"the request for your credit card name {card_name} has been approved by the branch manager"
        messages = "INSERT INTO bank_messages(customer_id,branch_id,messages,user_type,message_type,date) VALUES (%s, %s, %s,'customer','bank',%s)"
        messages_values = (cid, branch_id,messages_bank,date1)
        cursor.execute(messages, messages_values)
        cursor.execute("SELECT count FROM bankproducts WHERE customer_id = %s", (cid,))
        existing_record = cursor.fetchone()
        cursor.execute("delete from bank_messages where user_type='manager' and branch_id = (SELECT branch_id FROM employee WHERE employe_id = '%s')"% (session['mid']))
        if existing_record:  
            count = existing_record[0] + 1
            cursor.fetchall()
            cursor.execute("UPDATE bankproducts SET count = %s WHERE customer_id = %s", (count, cid))
        else:
            cursor.execute("INSERT INTO bankproducts (customer_id, count) VALUES (%s, %s)", (cid, 1))   
        flash('Approve successfully !')
        return redirect(url_for('manager.managerviewcreditcard'))
        
    if action=="reject":
        date = datetime.datetime.now()
        cursor.execute("SELECT customer_id,card_name FROM o_credit_card_request WHERE branch_id = (SELECT branch_id FROM employee WHERE employe_id = '%s') AND o_request_id='%s'"% (session['mid'],id))
        customer_details = cursor.fetchone()
        cid=customer_details[0]
        card_name = customer_details[1]

        cursor.execute("SELECT cid, branch_id, dob FROM customers WHERE branch_id=(SELECT branch_id FROM employee WHERE employe_id='%s') AND cid='%s'" % (session['mid'],cid))
        result = cursor.fetchone()
        # cid = result[0]
        branch_id = result[1]
        dob = result[2]

        cursor.fetchall()
        cursor.execute("update o_credit_card_request set status='reject' where o_request_id='%s'"%(id))
        messages_bank1=f"the request for your credit card name {card_name} has been decined by the branch manager for any assist call the branch"
        messages1 = "INSERT INTO bank_messages(customer_id,branch_id,messages,user_type,message_type,date) VALUES (%s, %s, %s,'customer','bank',%s)"
        messages_values1 = (cid, branch_id,messages_bank1,date)
        cursor.execute(messages1, messages_values1)
        cursor.execute("delete from bank_messages where user_type='manager' and branch_id = (SELECT branch_id FROM employee WHERE employe_id = '%s')"% (session['mid']))
        flash('Rejected successfully !')
        return redirect(url_for('manager.managerviewcreditcard'))

    return render_template('managerviewcreditcard.html',credit_card=credit_card,name12=name12)       


@manager.route('/managerviewcreditcardholders')
def managerviewcreditcardholders():
    cursor = db.cursor()
    cursor.execute("select employe_fname,employee_lname,email,image from employee where loginid='%s'"%(session['logid']))
    name12 = cursor.fetchall()
    # cursor.execute("SELECT card_name, job_type, c_name, c_location, m_salary, file1, file2, file3, date, status FROM o_credit_card_request WHERE branch_id = (SELECT branch_id FROM employee WHERE employe_id = '%s')" % (session['mid']))
    cursor.execute("SELECT c.fname, c.lname,c.photo,c.phone,c.email,cu.card_name,cu.card_limit,cu.status FROM customers c INNER JOIN credit_card cu ON c.cid = cu.customer_id WHERE c.branch_id = (SELECT branch_id FROM employee WHERE employe_id = '%s')"% (session['mid']))
    credit_card_holders = cursor.fetchall()

   

    return render_template('managerviewcreditcardholders.html',credit_card_holders=credit_card_holders,name12=name12)



@manager.route('/managerviewchurncustomer',methods=['POST' ,'GET'])
def managerviewchurncustomer():
    cursor = db.cursor()
    cursor.execute("select employe_fname,employee_lname,email,image from employee where loginid='%s'"%(session['logid']))
    name12 = cursor.fetchall()
    cursor.execute("SELECT c.cid,c.fname, c.lname,c.photo,c.phone,c.email,cu.leave_or_not FROM customers c INNER JOIN churn_customers cu ON c.cid = cu.customer_id WHERE c.branch_id = (SELECT branch_id FROM employee WHERE employe_id = '%s')"% (session['mid']))
    churn_cutomers = cursor.fetchall()
    date=datetime.datetime.now()

    if 'add' in request.form:
       
        messages=request.form['messages']
        customer_id=request.form['customer_id']
        min_allowed_time =  date - timedelta(hours=1)
        cursor.execute("SELECT MAX(date) FROM bank_messages WHERE customer_id = %s", (customer_id,))
        last_submission_time = cursor.fetchone()[0]
        cursor.execute("select branch_id from customers where cid='%s'" % customer_id)
        details=cursor.fetchone()
        print(details)
        branch_id=details[0]
        
        if last_submission_time is None or last_submission_time < min_allowed_time:
            bank_messages="INSERT INTO bank_messages(customer_id,branch_id,messages,user_type,message_type,date)  VALUES ( %s, %s, %s,'customer','bank',%s)"
            bank_messages_values = (customer_id, branch_id,messages,date)
            cursor.execute(bank_messages, bank_messages_values)
            # cursor.execute("SELECT * FROM customers where branch_id=(select branch_id from employee where employe_id='%s')"%(session['mid']))
            # employees = cursor.fetchall()
            flash("successfully send notification")
        else:
            print('send after 1 hoursuccess')

   

    return render_template('managerviewchurncustomer.html',churn_cutomers=churn_cutomers,name12=name12)



@manager.route('/userprofile', methods=['POST', 'GET'])
def userprofile():
    cursor = db.cursor()
    cursor.execute("select employe_fname,employee_lname,email,image from employee where loginid='%s'"%(session['logid']))
    name12 = cursor.fetchall()
    cursor.execute("SELECT * FROM employee WHERE employe_id = %s" % (session['mid']))
    details = cursor.fetchall()
    cursor.execute("SELECT password FROM login WHERE loginid = %s" % (session['logid']))
    password = cursor.fetchone()[0]
    print(details)
    logged_in_user_id=session['mid']
    if request.method == 'POST':
        if 'add' in request.form:
            image = request.files['file']
            if image:
                img = "uploads/" + str(uuid.uuid4()) + image.filename
                image.save('bank/static/' + img)
                cursor.execute("UPDATE employee SET image = %s WHERE loginid = %s", (img, session['logid']))
                flash("Photo updated successfully")
            else:
                flash("No photo selected")
            return redirect(url_for('manager.userprofile'))
    if request.method == 'POST':
        if 'add1' in request.form:
            
            newpassword=request.form['confirmpassword']
            if newpassword:
                cursor.execute("UPDATE login SET password = '%s' where loginid='%s'"%(newpassword,session['logid']))
                flash("password updated sucessfully")
                return redirect(url_for('public.login'))
            else:
                flash("No password selected")
            return redirect(url_for('manager.userprofile'))

    return render_template('userprofile.html',details=details,password=password,logged_in_user_id=logged_in_user_id,name12=name12)

@manager.route('/managerviewacc')
def managerviewacc():
    cursor = db.cursor()
    cursor.execute("select employe_fname,employee_lname,email,image from employee where loginid='%s'"%(session['logid']))
    name12 = cursor.fetchall()
    
    cursor.execute("""
    SELECT l.acc_type, l.acc_no, l.date_issued, c.fname, c.lname,c.photo,c.email,c.phone,l.acc_status,l.ifsccode
    FROM loanacc l, customers c
    WHERE l.customer_id = c.cid
    UNION
    SELECT s.acc_type, s.acc_no, s.acc_started_date, c.fname, c.lname,c.photo,c.email,c.phone,s.acc_status,s.ifsccode
    FROM savingsacc s, customers c
    WHERE s.customer_id = c.cid
    UNION
    SELECT d.acc_type, d.acc_no, d.deposit_date, c.fname, c.lname,c.photo,c.email,c.phone,d.acc_status,d.ifsccode
    FROM depositacc d, customers c
    WHERE d.customer_id = c.cid AND acc_status='active'
    AND d.branch_id = (SELECT branch_id FROM employee WHERE employe_id = %s)
    """, (session['mid'],))
    employees = cursor.fetchall()
    print(employees)
    return render_template('managerviewacc.html',employees=employees,name12=name12)



@manager.route('/managerviewemployee')
def managerviewemployee():
    cursor = db.cursor()
    cursor.execute("select employe_fname,employee_lname,email,image from employee where loginid='%s'"%(session['logid']))
    name12 = cursor.fetchall()
    
    cursor.execute("""
    select * from employee where employee='clerk' and  status='active' and branch_id = (SELECT branch_id FROM employee WHERE employe_id = '%s')
    """, (session['mid'],))
    employees = cursor.fetchall()
    print(employees)
    if "action" in request.args:
        action=request.args['action']
       
        id=request.args['delete_id']
    else:
        action="none"

        
    if action=="reject":
       
        cursor.execute("update employee set status='reject' where loginid='%s'"%(id))
        cursor.execute("update login set status='reject' where loginid='%s'"%(id))
        
        flash('Rejected successfully !')
        return redirect(url_for('manager.managerviewemployee'))
    return render_template('managerviewemployee.html',employees=employees,name12=name12)