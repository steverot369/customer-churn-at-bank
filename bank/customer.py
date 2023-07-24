from email import encoders
from email.mime.base import MIMEBase
from io import BytesIO
import uuid
from flask import *
from database import *
from datetime import datetime,timedelta
import random
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="bank"
)
customer=Blueprint('customer',__name__)

@customer.route('/customerhome',methods=['post', 'get'])
def customerhome():
    # data={}
    cursor = db.cursor()
    months = [
        'January', 'February', 'March', 'April',
        'May', 'June', 'July', 'August', 'September',
        'October', 'November', 'December'
    ]
    cursor = db.cursor()
    cursor.execute("SELECT MONTH(date_time), SUM(amount) FROM transaction where customer_id='%s' GROUP BY MONTH(date_time)"%(session['cust_id']))
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
   
    cursor.execute("SELECT t.t_no,t.t_type,t.amount,t.balance,t.date_time,s.acc_no from transaction t,savingsacc s where t.acc_id=s.savings_id and t.customer_id='%s'"%(session['cust_id']))
    transaction = cursor.fetchall()
    cursor.execute("select acc_no from savingsacc where customer_id='%s'"%(session['cust_id']))
    account_details = [row[0] for row in cursor.fetchall()]
    cursor.fetchall()
    cursor.execute("select fname,lname,email,photo from customers where loginid='%s'"%(session['logid']))
    name = cursor.fetchall()
    cursor.execute("select cid,branch_id from customers where cid='%s'"%(session['cust_id']))
    customer=cursor.fetchone()
    cid=customer[0]
    bid=customer[1]
    date = datetime.now()
    cursor.execute("select balance,acc_no,ifsccode from savingsacc where customer_id='%s'"%(session['cust_id']))
    customer_details=cursor.fetchall()
# begining


    # cursor.execute("select count from bankproducts where customer_id='%s'"%(session['cust_id']))
    # count=cursor.fetchone()[0]



    cursor.execute("SELECT dob FROM customers WHERE cid='%s'" % session['cust_id'])
    customer_detail = cursor.fetchone()
    dob = customer_detail[0]

    cursor.execute("SELECT count FROM bankproducts WHERE customer_id='%s'" % session['cust_id'])
    customer_details1 = cursor.fetchone()
    NumOfProducts = customer_details1[0]
 
        
    cursor.execute("SELECT COUNT(customer_id) FROM transaction WHERE customer_id='%s'" % session['cust_id'])
    customer_details3 = cursor.fetchone()
    IsActiveMember = customer_details3[0]



    # cursor.execute("SELECT status FROM credit_card WHERE customer_id='%s'" % session['cust_id'])
    # customer_details4 = cursor.fetchone()

    # try:
    #     credit_status = customer_details4[0]
    #     credit_status = 1 if credit_status == "approve" else 0
    # except TypeError:
    #     credit_status = 0  

    # print("credit==================", credit_status)


    cursor.execute("SELECT sum(penality_count) FROM loanacc WHERE customer_id='%s'" % (session['cust_id']))
    penality_result = cursor.fetchone()

    if penality_result:
        penality = penality_result[0]
    else:
        penality = 0

    
    

    current_date = datetime.now().date()
    dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
    age = (current_date - dob_date).days // 365
    
    
    
    
  
    
    
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


# end



    cursor.execute("SELECT from_acc, to_acc, amount,t_type, date FROM o_transaction WHERE customer_id = '%s' LIMIT 4" % (session['cust_id']))

    transaction_details=cursor.fetchall()

   
    logged_in_user_id=int(session['cust_id'])
    print("login_id=====",logged_in_user_id)

    
    cursor.execute("SELECT customer_id, reciever_id,amount,date,name,photo,from_name,from_photo FROM o_transaction where customer_id=%s or reciever_id=%s ORDER BY date DESC LIMIT 5"%(logged_in_user_id,logged_in_user_id))
    details = cursor.fetchall()
    current_datetime = datetime.now()

# Extract the date portion from the current date and time
    current_date = current_datetime.date()
    cursor.execute("SELECT customer_id, reciever_id, amount, date, name, photo, from_name, from_photo FROM o_transaction WHERE (customer_id = %s OR reciever_id = %s) ORDER BY date DESC LIMIT 3", (logged_in_user_id, logged_in_user_id))

    details1 = cursor.fetchall()

    cursor.execute("SELECT messages,date FROM bank_messages where message_type='bank' AND DATE(date) = '%s' AND (customer_id='%s' OR customer_id='0') AND user_type='customer'  ORDER BY date DESC LIMIT 3"%(current_date,session['cust_id']))
    bank_messages = cursor.fetchall()

    cursor.execute("SELECT messages,date,message_type FROM bank_messages where message_type='credit' AND DATE(date) = '%s' AND (customer_id='%s' OR customer_id='0') AND user_type='customer'  ORDER BY date DESC LIMIT 3"%(current_date,session['cust_id']))
    bank_messages1 = cursor.fetchall()

    cursor.execute("SELECT messages,date FROM bank_messages where customer_id='%s' AND DATE(date) = '%s' AND user_type='customer' and message_type='loan' ORDER BY date DESC LIMIT 3"%(session['cust_id'],current_date))
    bank_messages2 = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM bank_messages WHERE (message_type='bank') AND DATE(date) = '%s' AND (customer_id='%s' OR customer_id='0') AND user_type='customer'" % (current_date, session['cust_id']))
    messages_count = cursor.fetchone()[0]


    cursor.execute("select count from login where loginid='%s'"%(session['logid']))
    logindetails=cursor.fetchone()
    newusername=logindetails[0]
    
   

   
    if 'add' in request.form:
        messages=request.form['messages']
# Calculate the minimum allowed submission time (1 hour ago from the current time)
        min_allowed_time =  date - timedelta(hours=1)

        # Query the database to check the last submission time
        cursor.execute("SELECT MAX(date_time) FROM feedbacks WHERE customer_id = %s", (cid,))
        last_submission_time = cursor.fetchone()[0]

        # If the last submission time is None or earlier than the minimum allowed time, allow the submission
        if last_submission_time is None or last_submission_time < min_allowed_time:
            # Insert the feedback into the database
            feedback = "INSERT INTO feedbacks (customer_id, branch_id, messages, date_time) VALUES (%s, %s, %s, %s)"
            feedback_values = (cid, bid, messages, date)
            cursor.execute(feedback, feedback_values)
            flash('success')
        else:
            print('send after 1 hoursuccess')
   
    if 'add1' in request.form:
        messages=request.form['comments']

        min_allowed_time =  date - timedelta(hours=1)

     
        cursor.execute("SELECT MAX(date_time) FROM complaints WHERE customer_id = %s", (cid,))
        last_submission_time = cursor.fetchone()[0]

      
        if last_submission_time is None or last_submission_time < min_allowed_time:
           
            complaint = "INSERT INTO complaints (customer_id, branch_id, messages,reply ,date_time) VALUES (%s, %s, %s,'0', %s)"
            complaint_values = (cid, bid, messages, date)
            cursor.execute(complaint, complaint_values)
            flash('success')
        else:
            print('send after 1 hoursuccess')
    return render_template('customerhome.html',transaction=transaction,name=name,customer_details=customer_details,credit_score=credit_score,labels=labels, values=values,transaction_details=transaction_details,
    details=details,details1=details1,logged_in_user_id=logged_in_user_id,
    bank_messages=bank_messages,account_details=account_details,bank_messages1=bank_messages1,
    newusername=newusername,bank_messages2=bank_messages2,messages_count=messages_count)



@customer.route('/customerviewtransaction')
def customerviewtransaction():
    # data={}
    cursor = db.cursor()
    cursor.execute("select fname,lname,photo from customers where cid='%s'"%(session['cust_id']))
    name1 = cursor.fetchall()

    cursor.execute("SELECT t.t_no,t.t_type,t.amount,t.balance,t.date_time,s.acc_no from transaction t,savingsacc s where t.acc_id=s.savings_id and t.customer_id='%s' order by t.transaction_id DESC"%(session['cust_id']))
    transaction = cursor.fetchall()
    cursor.execute("select acc_no from savingsacc where customer_id='%s'"%(session['cust_id']))
    account_details = [row[0] for row in cursor.fetchall()]
    return render_template('customerviewtransaction.html',transaction=transaction,account_details=account_details,name1=name1)


@customer.route('/customerviewaccount')
def customerviewaccount():
    # data={}
    cursor = db.cursor()
    cursor.execute("select fname,lname,photo from customers where cid='%s'"%(session['cust_id']))
    name1 = cursor.fetchall()
    cursor.execute("SELECT acc_no,balance,acc_started_date from savingsacc where customer_id=(select cid from customers where cid='%s')"%(session['cust_id']))
    accounts = cursor.fetchall()
    return render_template('customerviewaccount.html',accounts=accounts,name1=name1)


@customer.route('/customertransferfund',methods=['post', 'get'])
def customertransferfund():
    # data={}
    cursor = db.cursor()
    cursor.execute("select fname,lname,photo from customers where cid='%s'"%(session['cust_id']))
    name1 = cursor.fetchall()

    cursor.execute("SELECT acc_no,balance,ifsccode from savingsacc where customer_id=(select cid from customers where cid='%s')"%(session['cust_id']))
    acc_no = cursor.fetchall()
    # cursor.execute("SELECT pin_no from savingsacc where customer_id='%s'"%(session['cust_id']))
    # pin_no = cursor.fetchone()[0]
   
    if 'add1' in request.form:
        acc_no=request.form['accno']
        confirmpin = request.form['confirmpin']
        cursor.execute("UPDATE savingsacc SET pin_no = %s WHERE acc_no = %s",(confirmpin, acc_no,))
        flash("successful Set Pin...")
        return redirect(url_for('customer.customertransferfund'))
    if 'add' in request.form:
        accno=request.form['accno']
        # from_acc = request.form['acc']
        to_acc = request.form['acc1']
        amount=int(request.form['amount'])
        pin=request.form['mpipin']
        # balance_transaction=request.form['balance']
        

        print("pin == ",pin)
        print("amount= ",amount)
        print("our account",acc_no)
        cursor.execute("select c.cid,c.fname,c.lname,photo from savingsacc s,customers c  where s.customer_id=c.cid and acc_no='%s'"%(to_acc))
        customer_details=cursor.fetchone()
        receiver_id=customer_details[0]
        fname=customer_details[1]
        lname=customer_details[2]
        full_name = fname + ' ' + lname
        photo=customer_details[3]


        cursor.execute("select c.cid,c.fname,c.lname,c.photo from savingsacc s,customers c  where s.customer_id=c.cid and acc_no=%s",(accno,))
        customer_details1=cursor.fetchone()
        # receiver_id=customer_details1[0]
        fname1=customer_details1[1]
        lname1=customer_details1[2]
        full_name1 = fname1 + ' ' + lname1
        photo1=customer_details1[3]


       


        print("receiver_id================",receiver_id)
        cursor.execute("select pin_no,balance,customer_id,branch_id,savings_id from savingsacc where acc_no='%s'"%(accno))
        mpipin=cursor.fetchone()
        balance=mpipin[1]
        cid=mpipin[2]
        branch_id=mpipin[3]
        savings_id=mpipin[4]
        
        date = datetime.now()
        trans_no = str(random.randint(1000000000000000, 9999999999999999))
       
        print(mpipin[0])
        calculate_balance=balance-amount
        print("caldddddd======",calculate_balance)

        if mpipin[0] == '1':
            flash("set mpi pin...")
            return redirect(url_for('customer.customersetpin'))
        elif mpipin[0] == pin:
            cursor.execute("UPDATE savingsacc SET balance = balance + %s WHERE acc_no = %s",(amount, to_acc,))
            cursor.execute("UPDATE savingsacc SET balance = balance - %s WHERE acc_no = %s",(amount, accno,))
            transaction = "INSERT INTO o_transaction (acc_id, customer_id,reciever_id, branch_id, from_acc, to_acc,name,photo,from_name,from_photo,amount,t_type, t_no, date) VALUES (%s, %s, %s,%s, %s,%s, %s,%s,%s, %s, %s, 'online', %s, %s)"
            transaction_values = (savings_id, cid,receiver_id, branch_id, accno, to_acc,full_name,photo,full_name1,photo1, amount,trans_no, date)
            cursor.execute(transaction, transaction_values)

 
            transaction1 = "INSERT INTO transaction (customer_id,acc_id,branch_id,t_no,t_type,amount,balance, date_time) VALUES (%s, %s,%s, %s, 'online',%s,%s,%s)"
            transaction_values1 = (cid,savings_id,branch_id,trans_no,amount,calculate_balance,date)
            cursor.execute(transaction1, transaction_values1) 

            flash("success...")
            return redirect(url_for('customer.customertransferfund'))
        
        else:
            flash("wrong pin")
            return redirect(url_for('customer.customertransferfund'))
        
    return render_template('customertransferfund.html',acc_no=acc_no,name1=name1)


@customer.route('/customersetpin',methods=['post', 'get'])
def customersetpin():
    # data={}
    cursor = db.cursor()
    cursor.execute("select fname,lname,photo from customers where cid='%s'"%(session['cust_id']))
    name1 = cursor.fetchall()
    cursor.execute("SELECT acc_no from savingsacc where pin_no='1' and customer_id=(select cid from customers where cid='%s')"%(session['cust_id']))
    acc_no = cursor.fetchall()
    if 'add' in request.form:
        acc_no=request.form['accno']
        confirmpin = request.form['confirmpin']
        cursor.execute("UPDATE savingsacc SET pin_no = %s WHERE acc_no = %s",(confirmpin, acc_no,))
        flash("successful Set Pin...")
        return redirect(url_for('customer.customersetpin'))
    return render_template('customersetpin.html',acc_no=acc_no,name1=name1)





@customer.route('/customerviewloanpayments')
def customerviewloanpayments():
    # data={}
    cursor=db.cursor()
    cursor.execute("select fname,lname,photo from customers where cid='%s'"%(session['cust_id']))
    name1 = cursor.fetchall()
    date = datetime.now().date()
    formatted_date = date.strftime("%d-%m-%y")
    print("date=======",formatted_date)
    cursor.execute("select acc_no,ifsccode,loan_type,maturity_date,interest_rate,interst_amt,issued_amount,remaing_amount,date_interest from loanacc where customer_id=(select cid from customers where cid='%s')"%(session['cust_id']))
    loan=cursor.fetchall()
    
    return render_template('customerviewloanpayments.html',loan=loan,formatted_date=formatted_date,name1=name1)




@customer.route('/customerrequestcreditcard',methods=['post','get'])
def customerrequestcreditcard():
    # data={}
    cursor=db.cursor()
    cursor.execute("select fname,lname,photo from customers where cid='%s'"%(session['cust_id']))
    name1 = cursor.fetchall()
    cursor.execute("select fname,lname,dob,gender,phone,email,city,state,zipcode,country,msalary,idnumber,address from customers where cid='%s'"%(session['cust_id']))
    customer=cursor.fetchall()

    cursor.execute("select fname,lname from customers where cid='%s'"%(session['cust_id']))
    customer_details=cursor.fetchone()
    fname=customer_details[0]
    lname=customer_details[1]
    full_name=fname + ' ' + lname


    card_name = request.args.get('card_name')
    salary = request.args.get('salary')
    if 'add' in request.form:
        # card_name=request.form['cardname']
        jobname = request.form['j_name']
        company_name = request.form['c_name']
        company_location = request.form['c_location']
        m_salary = request.form['msalary']

        i1=request.files['file1']
        img1="uploads/"+str(uuid.uuid4())+i1.filename
        i1.save('bank/static/'+img1)

        i2=request.files['file2']
        img2="uploads/"+str(uuid.uuid4())+i2.filename
        i2.save('bank/static/'+img2)

        i3=request.files['file3']
        img3="uploads/"+str(uuid.uuid4())+i3.filename
        i3.save('bank/static/'+img3)

        request_date = datetime.now().date()  # Get current date
       
        cursor.execute("select cid from customers where cid='%s'"%(session['cust_id']))
        cid=cursor.fetchone()[0]
        cursor.execute("select branch_id from customers where cid='%s'"%(session['cust_id']))
        bid=cursor.fetchone()[0]
        credit_card = "INSERT INTO o_credit_card_request(customer_id,branch_id,card_name,job_type,c_name,c_location,m_salary,file1,file2,file3,date,status) VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s, %s,%s,'pending')"
        credit_card_values = (cid, bid, card_name, jobname,company_name, company_location, m_salary, img1, img2,img3,request_date)
        cursor.execute(credit_card, credit_card_values)
        date=datetime.now()
        messages_bank=f"you have a new credit card request from {full_name}"
        messages = "INSERT INTO bank_messages(customer_id,branch_id,messages,user_type,message_type,date) VALUES (%s, %s, %s,'manager','bank',%s)"
        messages_values = (cid, bid,messages_bank,date)
        cursor.execute(messages, messages_values)


        
        flash("request successful...")

    
        return redirect(url_for('customer.customerrequestcreditcard'))
    
    return render_template('customerrequestcreditcard.html',customer=customer,card_name=card_name,salary=salary,name1=name1)

@customer.route('/differentcreditcard',methods=['post','get'])
def differentcreditcard():
    cursor=db.cursor()
    cursor.execute("select msalary from customers where cid='%s'"%(session['cust_id']))
    salary=cursor.fetchall()
    print(salary)
    return render_template('differentcreditcard.html',salary=salary)



@customer.route('/customersendfeedback')
def customersendfeedback():
    # data={}
 
    return render_template('customersendfeedback.html')




@customer.route('/customersendcomplaint')
def customersendcomplaint():
    # data={}
    cursor=db.cursor()
    cursor.execute("select cid,branch_id from customers where cid='%s'"%(session['cust_id']))
    customer=cursor.fetchone()
    cid=customer[0]
    bid=customer[1]
    current_datetime = datetime.now().date()
    formatted_datetime =datetime.strftime(current_datetime,"%d-%m-%y %H:%M:%S")

    if 'add' in request.form:
        messages=request.form['messages']
        complaint="insert into complaints(customer_id,branch_id,message,reply,date_time) values(%s,%s,%s,'0',%s)"
        complaint_values=(cid,bid,messages,formatted_datetime)
        cursor.execute(complaint,complaint_values)
    return render_template('customersendcomplaint.html')




@customer.route('/customerprofile', methods=['POST', 'GET'])
def customerprofile():
    cursor = db.cursor()
    cursor.execute("select fname,lname,photo from customers where cid='%s'"%(session['cust_id']))
    name1 = cursor.fetchall()
    cursor.execute("SELECT * FROM customers WHERE cid = %s" % (session['cust_id']))
    details = cursor.fetchall()
    cursor.execute("SELECT password FROM login WHERE loginid = %s" % (session['logid']))
    password = cursor.fetchone()[0]
    print(details)

    if request.method == 'POST':
        if 'add' in request.form:
            image = request.files['file']
            if image:
                img = "uploads/" + str(uuid.uuid4()) + image.filename
                image.save('bank/static/' + img)
                cursor.execute("UPDATE customers SET photo = %s WHERE loginid = %s", (img, session['logid']))
                flash("Photo updated successfully")
            else:
                flash("No photo selected")
            return redirect(url_for('customer.customerprofile'))
    if request.method == 'POST':
        if 'add1' in request.form:
            
            newpassword=request.form['confirmpassword']
            if newpassword:
                cursor.execute("UPDATE login SET password = '%s' where loginid='%s'"%(newpassword,session['logid']))
                flash("password updated sucessfully")
                return redirect(url_for('public.login'))
            else:
                flash("No password selected")
            return redirect(url_for('customer.customerprofile'))

    return render_template('customerprofile.html',details=details,password=password,name1=name1)




@customer.route('/customerpaysloan', methods=['POST', 'GET'])
def customerpaysloan():
        # data={}
    cursor = db.cursor()
    cursor.execute("select fname,lname,photo from customers where cid='%s'"%(session['cust_id']))
    name1 = cursor.fetchall()
    cursor.execute("SELECT acc_no,balance,ifsccode from savingsacc where customer_id=(select cid from customers where cid='%s')"%(session['cust_id']))
    acc_no = cursor.fetchall()
    cursor.execute("SELECT acc_no,loan_type,interst_amt,interest_rate,remaing_amount FROM loanacc where customer_id = '%s'"%(session['cust_id']))
    loan_account = cursor.fetchall()
    accountDetails = []  # Initialize accountDetails with a default value

    year = None
    month = None

    if 'add' in request.form:
        accno = request.form['accno']
        print(accno)
    
        cursor.execute("SELECT s.acc_no, s.ifsccode, s.balance, c.fname, c.lname, ch.debit_no, ch.cv, ch.expiry_date FROM customers c, savingsacc s, debitcard ch WHERE c.cid=s.customer_id AND s.savings_id=ch.savings_id AND s.acc_no = %s", (accno,))
        accountDetails = cursor.fetchall()
        print(accountDetails)
        cursor.execute("SELECT ch.expiry_date FROM customers c, savingsacc s, debitcard ch WHERE c.cid=s.customer_id AND s.savings_id=ch.savings_id AND s.acc_no = %s", (accno,))
        accountDetails1 = cursor.fetchone()
        
        if accountDetails1:
            expiry_date = accountDetails1[0]  # Assuming the expiry_date is in the format 'yyyy-mm-dd'
            expiry_date_parts = expiry_date.split('-')  # Split the date string into year, month, and day parts

            year = int(expiry_date_parts[0])
            month = int(expiry_date_parts[1])
            print("Year:", year)
            print("Month:", month)
    if 'add1' in request.form:
        loan_acc = request.form['loan_acc']
        savings_acc = request.form['savings_account']

        emi_amount = request.form['emi_amount']
        loanAmount = float(request.form['remaining_amount'])
        interestRate = float(request.form['interest_rate'])
        date = datetime.now().date()
        date1 = datetime.now()

        formatted_date = date.strftime("%d-%m-%y")
        interest_date = date + timedelta(days=30)
        interest_date_new=interest_date.strftime("%d-%m-%y")
        interestRate = interestRate / 100 / 12  # Convert to monthly interest rate
        monthlyinterest=loanAmount*interestRate
        principleAmount = float(emi_amount) - monthlyinterest

        outstandingBalance = int(loanAmount) - principleAmount
        print(interestRate)
        print(monthlyinterest)

        print(principleAmount)
        print(outstandingBalance)

        
        trans_no = str(random.randint(1000000000000000, 9999999999999999))
    
        cursor.execute("select loan_id,date_interest,customer_id,branch_id from loanacc where acc_no='%s'"%(loan_acc,))
        result1 = cursor.fetchone()
        if result1 is not None:
            loan_id = result1[0]
            interest_new_date = result1[1]
            cid = result1[2]
            bid = result1[3]

        else:
            # Handle the case when no matching record is found
            # For example, set default values or display an error message
            loan_id = None
            interest_new_date = None
            cid = None
            bid = None
        interest_new_date = datetime.strptime(interest_new_date, '%d-%m-%y').date()
        print(formatted_date)
        print(interest_new_date)
        
        if interest_new_date>=datetime.strptime(formatted_date, '%d-%m-%y').date():
            cursor.execute("UPDATE loanacc SET remaing_amount = %s ,date_interest = %s WHERE acc_no = %s",(outstandingBalance,interest_date_new, loan_acc,))
            loan="INSERT INTO loan_payment(customer_id,branch_id,loan_id,emi_paid,date_paid)  VALUES ( %s, %s,%s,%s,%s)"
            loan_values = (cid, bid, loan_id, emi_amount,formatted_date)
            cursor.execute(loan,loan_values)
            transaction = "INSERT INTO transaction (customer_id,acc_id,branch_id,t_no,t_type,amount,balance, date_time) VALUES (%s, %s,%s, %s, 'loan payment',%s,%s,%s)"
            transaction_values = (cid,loan_id,bid,trans_no,emi_amount,outstandingBalance,formatted_date)
            cursor.execute(transaction,transaction_values)
            cursor.execute("UPDATE savingsacc SET balance = balance - %s WHERE acc_no = %s",(emi_amount, savings_acc))
            bank_messages=f"you have paid your loan Emi Rs.{emi_amount}"

            messages = "INSERT INTO bank_messages (customer_id,branch_id,messages,user_type,message_type,date) VALUES (%s, %s, %s,'customer','loan',%s)"
            messages_values = (cid,bid,bank_messages,date1)
            cursor.execute(messages, messages_values)
            
            db.commit()  # Commit the changes to the database
            flash("emi paid successfully")
            return redirect(url_for('customer.customerpaysloan'))
        else:
            penality_count='1'
            cursor.execute("UPDATE loanacc SET remaing_amount = %s ,date_interest = %s,penality_count=penality_count + %s WHERE acc_no = %s",(outstandingBalance,interest_date_new,penality_count,loan_acc,))
            
            loan="INSERT INTO loan_payment(customer_id,branch_id,loan_id,emi_paid,date_paid)  VALUES ( %s, %s,%s,%s,%s)"
            loan_values = (cid, bid, loan_id, emi_amount,formatted_date)
            cursor.execute(loan,loan_values)
            transaction = "INSERT INTO transaction (customer_id,acc_id,branch_id,t_no,t_type,amount,balance, date_time) VALUES (%s, %s,%s, %s, 'loan payment',%s,%s,%s)"
            transaction_values = (cid,loan_id,bid,trans_no,emi_amount,outstandingBalance,formatted_date)
            cursor.execute(transaction,transaction_values)
            cursor.execute("UPDATE savingsacc SET balance = balance - %s WHERE acc_no = %s",(emi_amount,savings_acc))
            cursor.execute(transaction,transaction_values)
            cursor.execute("UPDATE savingsacc SET balance = balance - %s WHERE acc_no = %s",(emi_amount, savings_acc))
            bank_messages=f"you have paid your loan Emi Rs.{emi_amount}"

            messages = "INSERT INTO bank_messages (customer_id,branch_id,messages,user_type,message_type,date) VALUES (%s, %s, %s,'customer','loan',%s)"
            messages_values = (cid,bid,bank_messages,date1)
            cursor.execute(messages, messages_values)

            db.commit()  # Commit the changes to the database
            flash("emi paid successfully...also a penality")
            return redirect(url_for('customer.customerpaysloan'))
            
        
    return render_template('customerpaysloan.html', acc_no=acc_no, accountDetails=accountDetails, year=year, month=month,loan_account=loan_account,name1=name1)



@customer.route('/accountstatement', methods=['GET', 'POST'])
def accountstatement():
    cursor = db.cursor()
    cursor.execute("select fname,lname,photo from customers where cid='%s'"%(session['cust_id']))
    name1 = cursor.fetchall()
    cursor.execute("SELECT t_no, t_type, amount, balance, date_time FROM transaction WHERE customer_id = '%s'"%(session['cust_id']))
    transactions = cursor.fetchall()
    cursor.execute("select acc_no from savingsacc where customer_id='%s'"%(session['cust_id']))
    account_details=cursor.fetchall()
    date=datetime.now().date()
    if request.method == 'POST':
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')
        account = request.form.get('accno')


        # Convert the from_date and to_date to datetime objects for comparison
        from_date = datetime.strptime(from_date, '%Y-%m-%d')
        to_date = datetime.strptime(to_date, '%Y-%m-%d')

        # Fetch the transactions within the specified date range from the database
        cursor = db.cursor()
        cursor.execute("select savings_id,ifsccode from savingsacc where acc_no='%s'"%(account))
        account1=cursor.fetchone()
        savings_id=account1[0]
        ifsccode=account1[1]
        cursor.fetchall()
        cursor.execute("SELECT t_no, t_type, amount, balance, date_time FROM transaction WHERE customer_id = '%s' AND acc_id='%s' AND date_time BETWEEN '%s' AND '%s'"  % (session['cust_id'],savings_id, from_date, to_date))
        transactions = cursor.fetchall()
        cursor.execute("SELECT fname, lname, address, phone, email,branch FROM customers WHERE cid='%s'" % (session['cust_id']))
        customer_details = cursor.fetchone()
        fname = customer_details[0]
        lname = customer_details[1]

        full_name = fname + ' ' + lname
        address = customer_details[2]
        phone = customer_details[3]
        email = customer_details[4]
        branch = customer_details[5]

       
       

        # Generate the PDF using ReportLab
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        # Define styles
        styles = getSampleStyleSheet()
        customer_details_style = ParagraphStyle(
            'customer_details_style',
            parent=styles['Normal'],
            fontSize=12,
            leading=14,
            leftIndent=0,
            spaceAfter=12,
        )

        # Create the table to hold the transaction data
        table_data = [['Transaction No', 'Transaction Type', 'Amount', 'Balance', 'Date']]
        for transaction in transactions:
            table_data.append(list(transaction))

        table = Table(table_data)

        # Apply styling to the table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        # Build the PDF document
        elements = []

        # Add the logo at the top right
        logo = "C:/mca project 2023/BankManagement/bank/static/images/logo3.png"
        logo_image = Image(logo, width=90, height=30)
        logo_image.hAlign = 'LEFT'
        elements.append(logo_image)

        # Add customer details
        customer_details_table_data = [
           
            ['Date',date],
            ['Account Name:', full_name],
            ['Address:', address],
            ['Phone:', phone],
            ['Email:', email],
            ['Account No:', account],
            ['Ifsccode:', ifsccode],
            ['Branch',branch],


           

        ]
        customer_details_table = Table(customer_details_table_data)
        customer_details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
        ]))
        
        elements.append(customer_details_table)

        # Add spacer to align the transaction table
        elements.append(Spacer(1, 0.5 * inch))
        account_statements_message = f"Account Statements from {from_date} to {to_date}"
        elements.append(Paragraph(account_statements_message, styles['Normal']))
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(table)
        
        doc.build(elements)

        # Move the buffer's pointer to the beginning
        buffer.seek(0)

        # Create a Flask response with the PDF file data
        response = make_response(buffer.getvalue())

        # Set the Content-Disposition header to specify the attachment filename
        response.headers['Content-Disposition'] = 'attachment; filename=account_statement.pdf'

        # Set the appropriate MIME type for PDF
        response.mimetype = 'application/pdf'

        msg = MIMEMultipart()
        msg['From'] = 'mltalerts.mlt.co.in@gmail.com'
        msg['To'] = email  # Replace with the customer's email address
        msg['Subject'] = 'Account Statement'
        message = f"Your account statement from {from_date} {to_date}!."

        msg.attach(MIMEText(message, "plain"))
        # Attach the PDF file to the email
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(response.data)
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', 'attachment', filename='account_statement.pdf')
        msg.attach(attachment)

        # Send the email
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login('mltalerts.mlt.co.in@gmail.com', 'kjerrrtwgllsaqdp')  # Replace with your email credentials
            smtp.send_message(msg)

            # Send the response as a download
        flash("mail send successfully to your email")
        return redirect(url_for('customer.accountstatement'))

        


    return render_template('accountstatement.html', transactions=transactions,account_details=account_details,name1=name1)



@customer.route('/setusername',methods=['POST','GET'])
def setusername():
    cursor=db.cursor()
    cursor.execute("select fname,lname,photo from customers where cid='%s'"%(session['cust_id']))
    name1 = cursor.fetchall()
    cursor.execute("select uname from login")
    uname=[row[0] for row in cursor.fetchall()]
    cursor.execute("select count,login_type from login where loginid='%s'"%(session['logid']))
    logindetails=cursor.fetchone()
    count=logindetails[0]
    logintype=logindetails[1]
    print(logintype)
    cursor.fetchall()


    if 'add' in request.form:
        username=request.form['username']
        password=request.form['password']
        cursor.execute("UPDATE login SET uname='%s', password='%s', count='yes' WHERE loginid='%s'" % (username, password, session['logid']))
        flash("successfuly change username and password")
        return redirect(url_for('public.login'))

    return render_template('setusername.html',uname=uname,count=count,logintype=logintype,name1=name1)


@customer.route('/customeviewfixedpayments')
def customeviewfixedpayments():
    # data={}
    cursor=db.cursor()
    cursor.execute("select fname,lname,photo from customers where cid='%s'"%(session['cust_id']))
    name1 = cursor.fetchall()
    cursor.execute("select * from transaction where customer_id='%s' and t_type='fixed deposit'"%(session['cust_id']))
    interest=cursor.fetchall()

    return render_template('customeviewfixedpayments.html',interest=interest,name1=name1)

@customer.route('/publichome')
def publichome():
    session.clear()
    flash("Successfully logout...")
    return redirect(url_for('public.publichome'))