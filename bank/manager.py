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
    cursor.execute("select employe_fname,employee_lname,email from employee where loginid='%s'"%(session['logid']))
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
            bank_messages="INSERT INTO bank_messages(customer_id,branch_id,messages,date)  VALUES ( %s, %s, %s,%s)"
            bank_messages_values = (customer_id, branch_id,messages,date)
            cursor.execute(bank_messages, bank_messages_values)
            # cursor.execute("SELECT * FROM customers where branch_id=(select branch_id from employee where employe_id='%s')"%(session['mid']))
            # employees = cursor.fetchall()
            flash("successfully send notification")
        else:
            print('send after 1 hoursuccess')
        
    

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
    IsActiveMembervalue = 1 if IsActiveMember >= 5 else 0
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
        IsActiveMembervalue = 1 if IsActiveMember >= 15 else 0
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
            # churn = "INSERT INTO churn_customers(customer_id, branch_id, leave_or_not) VALUES (%s, %s, 'will leave')"
            # churn_values = (customer_id, branch_id)
            # cursor.execute(churn, churn_values)
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
            if NumOfProducts > NumOfProducts:
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
                                credit_status=credit_status, reason1=reason1,reason2=reason2,reason3=reason3,reason4=reason4,reason5=reason5)
        else:
            return render_template('predictionresult.html', prediction_text="The Customer will not leave the bank",
                                probability=stay_probability, stay_probability=probability,
                                customer_id=customer_id, customer_details=customer_details, age=age,
                                Geography_Germany=Geography_Germany, Geography_Spain=Geography_Spain,
                                tenure=tenure, msalary=msalary, NumOfProducts=NumOfProducts, balances=balances,
                                gender_value=gender_value, IsActiveMembervalue=IsActiveMembervalue,
                                credit_score=credit_score, f_name=f_name, l_name=l_name, state=state,
                                credit_status=credit_status)


    # Pass date and tenure to the template
    return render_template('managercustomerchurn.html', customer_id=customer_id, customer_details=customer_details, age=age,Geography_Germany=Geography_Germany,Geography_Spain=Geography_Spain,tenure=tenure,msalary=msalary,NumOfProducts=NumOfProducts,balances=balances,gender_value=gender_value,IsActiveMembervalue=IsActiveMembervalue,credit_score=credit_score,f_name=f_name,l_name=l_name,state=state,credit_status=credit_status)

@manager.route('/customerchurnprediction', methods=['POST'])
def customerchurnprediction():
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
                                   probability=probability, stay_probability=stay_probability)
        else:
            return render_template('predictionresult.html', prediction_text="The Customer will not leave the bank",
                                   probability=stay_probability, stay_probability=probability)
    return render_template('customerchurnprediction.html')





@manager.route('/managerviewloanacc',methods=['post','get'])
def clerkviewloanacc():

    cursor = db.cursor()
    cursor.execute("select employe_fname,employee_lname,email from employee where loginid='%s'"%(session['logid']))
    name = cursor.fetchall()
    cursor.execute("SELECT c.fname,c.lname,l.acc_no,l.ifsccode,l.interst_amt,l.interest_rate,l.issued_amount,l.remaing_amount,l.acc_status,l.date_interest,l.loan_type FROM customers c,loanacc l where c.cid=l.customer_id and l.branch_id=(select branch_id from employee where employe_id='%s')"%(session['mid']))
    employees = cursor.fetchall()
    date = datetime.now().date()
    formatted_date = date.strftime("%d-%m-%y")
    return render_template('managerviewloanacc.html',employees=employees,name=name,formatted_date=formatted_date)
    

@manager.route('/managerviewtransaction',methods=['post','get'])
def managerviewtransaction():

    cursor = db.cursor()
    cursor.execute("select employe_fname,employee_lname,email from employee where loginid='%s'"%(session['logid']))
    name = cursor.fetchall()
    cursor.execute("SELECT t.t_no,t.t_type,t.amount,t.date_time,c.fname,c.lname,s.acc_no from transaction t,customers c,savingsacc s where t.customer_id=c.cid AND t.customer_id=s.customer_id AND t.branch_id=(select branch_id from employee where employe_id='%s')"%(session['mid']))
    employees = cursor.fetchall()
    date = datetime.datetime.now().date()
    formatted_date = datetime.datetime.strftime(date,"%d-%m-%y")
    return render_template('managerviewtransaction.html',employees=employees,name=name,formatted_date=formatted_date)
        
          
@manager.route('/managerviewcreditcard')
def managerviewcreditcard():
    cursor = db.cursor()
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

        cursor.execute("SELECT cid, branch_id, dob FROM customers WHERE branch_id=(SELECT branch_id FROM employee WHERE employe_id='%s')" % (session['mid']))
        result = cursor.fetchone()
        cid = result[0]
        branch_id = result[1]
        dob = result[2]

        # Fetch all results before executing the next query
        cursor.fetchall()

        date = datetime.datetime.now().date()
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
        cursor.execute("SELECT count FROM bankproducts WHERE customer_id = %s", (cid,))
        existing_record = cursor.fetchone()
        if existing_record:  
            count = existing_record[0] + 1
            cursor.fetchall()
            cursor.execute("UPDATE bankproducts SET count = %s WHERE customer_id = %s", (count, cid))
        else:
            cursor.execute("INSERT INTO bankproducts (customer_id, count) VALUES (%s, %s)", (cid, 1))   
        flash('Approve successfully !')
        return redirect(url_for('manager.managerviewcreditcard'))
        
    if action=="reject":
        cursor.execute("update o_credit_card_request set status='reject' where o_request_id='%s'"%(id))
        flash('Rejected successfully !')
        return redirect(url_for('manager.managerviewcreditcard'))

    return render_template('managerviewcreditcard.html',credit_card=credit_card)       


@manager.route('/managerviewcreditcardholders')
def managerviewcreditcardholders():
    cursor = db.cursor()
    # cursor.execute("SELECT card_name, job_type, c_name, c_location, m_salary, file1, file2, file3, date, status FROM o_credit_card_request WHERE branch_id = (SELECT branch_id FROM employee WHERE employe_id = '%s')" % (session['mid']))
    cursor.execute("SELECT c.fname, c.lname,c.photo,c.phone,c.email,cu.card_name,cu.card_limit,cu.status FROM customers c INNER JOIN credit_card cu ON c.cid = cu.customer_id WHERE c.branch_id = (SELECT branch_id FROM employee WHERE employe_id = '%s')"% (session['mid']))
    credit_card_holders = cursor.fetchall()

   

    return render_template('managerviewcreditcardholders.html',credit_card_holders=credit_card_holders)



@manager.route('/managerviewchurncustomer')
def managerviewchurncustomer():
    cursor = db.cursor()
   
    cursor.execute("SELECT c.fname, c.lname,c.photo,c.phone,c.email,cu.leave_or_not FROM customers c INNER JOIN churn_customers cu ON c.cid = cu.customer_id WHERE c.branch_id = (SELECT branch_id FROM employee WHERE employe_id = '%s')"% (session['mid']))
    churn_cutomers = cursor.fetchall()

   

    return render_template('managerviewchurncustomer.html',churn_cutomers=churn_cutomers)



@manager.route('/userprofile', methods=['POST', 'GET'])
def userprofile():
    cursor = db.cursor()
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

    return render_template('userprofile.html',details=details,password=password,logged_in_user_id=logged_in_user_id)