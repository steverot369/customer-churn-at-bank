from flask import *
from database import *
from datetime import datetime
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
    cursor.execute("SELECT dob, msalary, state, date,gender,active,f_name,l_name FROM customers WHERE cid='%s'" % customer_id)
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

    current_date = datetime.today().date()
    dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
    age = (current_date - dob_date).days // 365
    today = datetime.today().date()
    date_date = datetime.strptime(joindate, "%Y-%m-%d").date()
    tenure = today.year - date_date.year - ((today.month, today.day) < (date_date.month, date_date.day))
    NumOfProducts = customer_details1[0]
    balances = customer_balances[1]
    # balances = [balance[1] for balance in customer_balances]
    IsActiveMember = customer_details3[0]
    IsActiveMembervalue = 1 if IsActiveMember >= 5 else 0
    if IsActiveMember >=3 and IsActiveMember <=10:
        credit_score = random.randint(300, 350)
    elif IsActiveMember >=11 and IsActiveMember <=20:
        credit_score = random.randint(351, 450)
    elif IsActiveMember >=21 and IsActiveMember <=30:
        credit_score = random.randint(451, 550)
    elif IsActiveMember >=31 and IsActiveMember <=40:
        credit_score = random.randint(551, 650)
    elif IsActiveMember >=41 and IsActiveMember <=50:
        credit_score = random.randint(651, 700)
    elif IsActiveMember >=51 and IsActiveMember <=60:
        credit_score = random.randint(701, 750)
    elif IsActiveMember >=61 and IsActiveMember <=70:
        credit_score = random.randint(751, 800)
    elif IsActiveMember >=71 and IsActiveMember <=80:
        credit_score = random.randint(801, 850)
    elif IsActiveMember >=81 and IsActiveMember <=90:
        credit_score = random.randint(851, 900)
    else:
        credit_score = random.randint(901, 950)

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
        cursor.execute("SELECT dob, msalary, state, date,gender active FROM customers WHERE cid='%s'" % customer_id)
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
        state = customer_details[2]


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

        current_date = datetime.today().date()
        dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
        age = (current_date - dob_date).days // 365
        today = datetime.today().date()
        date_date = datetime.strptime(joindate, "%Y-%m-%d").date()
        tenure = today.year - date_date.year - ((today.month, today.day) < (date_date.month, date_date.day))
        NumOfProducts = customer_details1[0]
        balances = customer_balances[1]
        # balances = [balance[1] for balance in customer_balances]
        IsActiveMember = customer_details3[0]
        IsActiveMembervalue = 1 if IsActiveMember >= 5 else 0
        if IsActiveMember >=3 and IsActiveMember <=10:
            credit_score = random.randint(300, 350)
        elif IsActiveMember >=11 and IsActiveMember <=20:
            credit_score = random.randint(351, 450)
        elif IsActiveMember >=21 and IsActiveMember <=30:
            credit_score = random.randint(451, 550)
        elif IsActiveMember >=31 and IsActiveMember <=40:
            credit_score = random.randint(551, 650)
        elif IsActiveMember >=41 and IsActiveMember <=50:
            credit_score = random.randint(651, 700)
        elif IsActiveMember >=51 and IsActiveMember <=60:
            credit_score = random.randint(701, 750)
        elif IsActiveMember >=61 and IsActiveMember <=70:
            credit_score = random.randint(751, 800)
        elif IsActiveMember >=71 and IsActiveMember <=80:
            credit_score = random.randint(801, 850)
        elif IsActiveMember >=81 and IsActiveMember <=90:
            credit_score = random.randint(851, 900)
        else:
            credit_score = random.randint(901, 950)
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
        if prediction == 1:
            return render_template('predictionresult.html', prediction_text="The Customer will leave the bank",
                                   probability=probability, stay_probability=stay_probability,customer_id=customer_id, customer_details=customer_details, age=age,Geography_Germany=Geography_Germany,Geography_Spain=Geography_Spain,tenure=tenure,msalary=msalary,NumOfProducts=NumOfProducts,balances=balances,gender_value=gender_value,IsActiveMembervalue=IsActiveMembervalue,credit_score=credit_score,f_name=f_name,l_name=l_name,state=state)
        else:
            return render_template('predictionresult.html', prediction_text="The Customer will not leave the bank",
                                   probability=stay_probability, stay_probability=probability,customer_id=customer_id, customer_details=customer_details, age=age,Geography_Germany=Geography_Germany,Geography_Spain=Geography_Spain,tenure=tenure,msalary=msalary,NumOfProducts=NumOfProducts,balances=balances,gender_value=gender_value,IsActiveMembervalue=IsActiveMembervalue,credit_score=credit_score,f_name=f_name,l_name=l_name,state=state)

    # Pass date and tenure to the template
    return render_template('managercustomerchurn.html', customer_id=customer_id, customer_details=customer_details, age=age,Geography_Germany=Geography_Germany,Geography_Spain=Geography_Spain,tenure=tenure,msalary=msalary,NumOfProducts=NumOfProducts,balances=balances,gender_value=gender_value,IsActiveMembervalue=IsActiveMembervalue,credit_score=credit_score,f_name=f_name,l_name=l_name,state=state)

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
    

        
          
        